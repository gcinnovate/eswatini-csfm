from .. import db, celery, INDICATORS
from ..models import FlowData, Location
from ..utils import get_indicators_from_rapidpro_results
from datetime import datetime
import calendar
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

MONTHS_DICT = dict((v, k) for k, v in enumerate(calendar.month_name))


@celery.task(name="tasks.save_flowdata")
def save_flowdata(request_args, request_json, districts, faclities):
    msisdn = request_args.get('msisdn')
    report_type = request_args.get('report_type')
    facility = request_args.get('facility')
    district = request_args.get('district')

    flowdata = get_indicators_from_rapidpro_results(
        request_json['results'], INDICATORS, report_type)
    month = flowdata.pop('month')
    if report_type in ('csfm'):
        year = datetime.now().year

    month_str = "{0}-{1:02}".format(year, MONTHS_DICT[month])

    # redis_client.districts set using @app.before_first_request
    ids = districts.get(district)
    if ids:
        logger.info(f'Going to save data for district: {district}, station: {station}')
        district_id = ids['id']
        if report_type in ('csfm'):
            logger.info(f'Handling Facility Data for MSISDN: {msisdn}')
            facility_id = faclities.get(facility)

            db.session.add(FlowData(
                msisdn=msisdn, district=district_id, facility=facility_id,
                report_type=report_type, month=month_str, year=year, values=flowdata))
            db.session.commit()

        logger.info(f'Done processing flow values')
    else:
        logger.info("district ids empty")