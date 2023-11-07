from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update, func, or_, and_
from sqlalchemy.orm import Session

from database import get_db
from models import Service
from schemas import ServiceGet, ServiceCreate, ServiceUpdate, Status

router = APIRouter(
    prefix='/service',
    tags=['service']
)


@router.post('/', response_model=ServiceCreate)
def create_service(new_service: ServiceCreate, db: Session = Depends(get_db)):
    # model_dump вместо dict
    stmt = insert(Service).values(**new_service.model_dump())
    db.execute(stmt)
    db.commit()
    return new_service


@router.get('/{service_name}', response_model=list[ServiceGet])
def get_service_by_name(service_name: str, db: Session = Depends(get_db)):
    # Изменить stmt, что бы выбирались последние записи по start_time
    stmt = select(Service).where(Service.name == service_name).order_by(Service.start_time.desc())
    service_list = db.execute(stmt).scalars().fetchall()
    return service_list


@router.get('/', response_model=list[ServiceGet])
def get_actual_service(db: Session = Depends(get_db)):
    # Изменить stmt, что бы выбирались последние записи по start_time
    subquery = (
        select(
            Service.name,
            func.max(Service.start_time).label('max_start_time')
        )
        .group_by(Service.name)
        .subquery()
    )
    query = (
        select(Service)
        .join(subquery, Service.name == subquery.c.name)
        .filter(Service.start_time == subquery.c.max_start_time)
    )
    service_list = db.execute(query).scalars().fetchall()
    return service_list


@router.put('/{service_id}')
def update_service(service_id: int, new_data: ServiceUpdate, db: Session = Depends(get_db)):
    stmt_first = update(Service).where(Service.id == service_id).values({
        'end_time': datetime.utcnow(),
    }).returning(Service.name)
    name = db.execute(stmt_first).scalar()
    data = {
        'name': name,
        'status': new_data.status,
        'description': new_data.description,
    }
    stmt_second = insert(Service).values(data)
    db.execute(stmt_second)
    db.commit()
    return data


@router.get('/info/')
def get_service_info(
        service_name: str,
        date_from: datetime = datetime.utcnow(),
        date_to: datetime = datetime.utcnow(),
        db: Session = Depends(get_db)
):
    name = service_name
    stmt = select(Service).where(
        and_(
            Service.name == name,
            or_(Service.start_time.between(date_from, date_to),
                Service.end_time.between(date_from, date_to))
        )).order_by(Service.start_time.desc())

    service_info = db.execute(stmt).scalars().fetchall()
    # информация о том сколько не работал сервис и считать SLA в процентах до 3-й запятой

    if service_info:
        downtime = None
        all_time = (date_to - date_from).total_seconds()
        for service in service_info:
            if downtime and service.status == Status.not_ok:
                downtime += (
                    service.end_time - service.start_time if service.end_time else
                    datetime.utcnow() - service.start_time
                )
            elif service.status == Status.not_ok:
                downtime = (
                    service.end_time - service.start_time if service.end_time else
                    datetime.utcnow() - service.start_time
                )

        if downtime:
            downtime_seconds = downtime.total_seconds()
            sla = round((100 * downtime_seconds) / all_time, 3)
        else:
            sla = 100

        resp = {
            'Время простоя': str(downtime) if downtime else 0,
            'SLA': f'{sla}%'
        }
        return resp
    else:
        return 'Перепроверьте введённые данные'


