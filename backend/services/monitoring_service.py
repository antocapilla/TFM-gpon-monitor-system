import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from database.mongo import monitoring_data_collection, monitoring_config_collection
from models.monitoring_model import ONTData, MonitoringConfig
from services.manager_service import ManagerService
from bson import ObjectId


logger = logging.getLogger(__name__)

class MonitoringService:
    @staticmethod
    def create_monitoring_data(data: List[ONTData]):
        ont_data_list = [ont_data.dict() for ont_data in data]
        monitoring_data_collection.insert_many(ont_data_list)

    @staticmethod
    def delete_monitoring_data(building: Optional[str] = None, 
                            floor: Optional[str] = None, 
                            serial: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"delete_monitoring_data called with building={building}, floor={floor}, serial={serial}")
        
        onts_to_query = []
        
        if serial:
            onts_to_query = [{"serial": serial}]
            logger.info(f"Deleting data for single ONT with serial: {serial}")
        elif floor and building:
            onts_to_query = ManagerService.get_onts_for_floor(building, floor)
            logger.info(f"Deleting data for {len(onts_to_query)} ONTs in building '{building}', floor '{floor}'")
        elif building:
            onts_to_query = ManagerService.get_onts_for_building(building)
            logger.info(f"Deleting data for {len(onts_to_query)} ONTs in building '{building}'")
        else:
            # Si no se proporciona ningún parámetro, obtener todas las ONTs
            onts_to_query = ManagerService.get_all_onts()
            logger.info(f"Deleting data for all {len(onts_to_query)} ONTs")
        
        if not onts_to_query:
            logger.warning("No ONTs found to delete data")
            return {
                "deleted_count": 0,
                "onts_affected": []
            }

        serials = [ont['serial'] for ont in onts_to_query]
        logger.info(f"ONT serials to delete data: {serials}")
        
        result = monitoring_data_collection.delete_many({'serial': {'$in': serials}})
        deleted_count = result.deleted_count
        
        logger.info(f"Deleted {deleted_count} documents for {len(serials)} ONTs")
        return {
            "deleted_count": deleted_count,
            "onts_affected": serials
        }

    @staticmethod
    def get_time_series_data(
        serial: Optional[str] = None,
        floor: Optional[str] = None,
        building: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = 'hour'
    ) -> List[Dict]:
        logger.info(f"get_time_series_data called with serial={serial}, floor={floor}, building={building}, start_date={start_date}, end_date={end_date}, interval={interval}")
        
        match = {}
        if serial:
            match['serial'] = serial
        elif floor and building:
            onts = ManagerService.get_onts_for_floor(building, floor)
            match['serial'] = {'$in': [ont['serial'] for ont in onts]}
        elif building:
            onts = ManagerService.get_onts_for_building(building)
            match['serial'] = {'$in': [ont['serial'] for ont in onts]}
        
        if start_date:
            match['timestamp'] = {'$gte': start_date}
        if end_date:
            match['timestamp'] = match.get('timestamp', {})
            match['timestamp']['$lte'] = end_date

        group_id = {
            'year': {'$year': '$timestamp'},
            'month': {'$month': '$timestamp'},
            'day': {'$dayOfMonth': '$timestamp'},
        }
        if interval == 'hour':
            group_id['hour'] = {'$hour': '$timestamp'}
        elif interval == 'minute':
            group_id['hour'] = {'$hour': '$timestamp'}
            group_id['minute'] = {'$minute': '$timestamp'}

        pipeline = [
            {'$match': match},
            {'$sort': {'timestamp': 1}},
            {'$group': {
                '_id': group_id,
                'timestamp': {'$last': '$timestamp'},
                'totalBytesReceived': {'$last': {'$sum': '$wans.bytesReceived'}},
                'totalBytesSent': {'$last': {'$sum': '$wans.bytesSent'}},
                'totalWifiBytesReceived': {'$last': {'$sum': '$wifi.totalBytesReceived'}},
                'totalWifiBytesSent': {'$last': {'$sum': '$wifi.totalBytesSent'}},
                'totalWifiAssociations': {'$last': {'$sum': '$wifi.totalAssociations'}},
                'activeWANs': {'$last': {'$size': {'$filter': {'input': '$wans', 'as': 'wan', 'cond': {'$eq': ['$$wan.connectionStatus', 'Connected']}}}}},
                'activeWiFiInterfaces': {'$last': {'$size': {'$filter': {'input': '$wifi', 'as': 'wifi', 'cond': {'$eq': ['$$wifi.status', 'Up']}}}}},
                'connectedHosts': {'$last': {'$size': '$hosts'}},
                'failedConnections': {'$last': {'$size': {'$filter': {'input': '$hosts', 'as': 'host', 'cond': {'$eq': ['$$host.active', False]}}}}},
                'deviceCount': {'$last': 1},
                'avgTransceiverTemperature': {'$avg': '$gpon.transceiverTemperature'},
                'avgRxPower': {'$avg': '$gpon.rxPower'},
                'avgTxPower': {'$avg': '$gpon.txPower'},
            }},
            {'$sort': {'_id': 1}}
        ]

        logger.info(f"Executing MongoDB aggregation pipeline: {pipeline}")
        results = list(monitoring_data_collection.aggregate(pipeline))
        logger.info(f"Aggregation result count: {len(results)}")

        formatted_results = []
        for result in results:
            formatted_result = {
                'timestamp': result['timestamp'],
                'totalBytesReceived': result['totalBytesReceived'],
                'totalBytesSent': result['totalBytesSent'],
                'totalWifiBytesReceived': result['totalWifiBytesReceived'],
                'totalWifiBytesSent': result['totalWifiBytesSent'],
                'totalWifiAssociations': result['totalWifiAssociations'],
                'activeWANs': result['activeWANs'],
                'activeWiFiInterfaces': result['activeWiFiInterfaces'],
                'connectedHosts': result['connectedHosts'],
                'failedConnections': result['failedConnections'],
                'deviceCount': result['deviceCount'],
                'avgTransceiverTemperature': result['avgTransceiverTemperature'],
                'avgRxPower': result['avgRxPower'],
                'avgTxPower': result['avgTxPower'],
            }
            formatted_results.append(formatted_result)

        logger.info(f"Returning {len(formatted_results)} time series data points")
        return formatted_results
    @staticmethod
    def get_latest_values(serial: Optional[str] = None, 
                        floor: Optional[str] = None, 
                        building: Optional[str] = None) -> Dict:
        logger.info(f"get_latest_values called with serial={serial}, floor={floor}, building={building}")
        
        onts_to_query = []
        
        if serial:
            onts_to_query = [{"serial": serial}]
            logger.info(f"Querying for single ONT with serial: {serial}")
        elif floor and building:
            onts_to_query = ManagerService.get_onts_for_floor(building, floor)
            logger.info(f"Retrieved {len(onts_to_query)} ONTs for building '{building}', floor '{floor}'")
        elif building:
            onts_to_query = ManagerService.get_onts_for_building(building)
            logger.info(f"Retrieved {len(onts_to_query)} ONTs for building '{building}'")
        else:
            # Si no se proporciona ningún parámetro, obtener todas las ONTs
            onts_to_query = ManagerService.get_all_onts()
            logger.info(f"Retrieved {len(onts_to_query)} ONTs in total")
        
        if not onts_to_query:
            logger.warning("No ONTs found to query")
            return {
                "timestamp": None,
                "totalBytesReceived": 0,
                "totalBytesSent": 0,
                "totalWifiAssociations": 0,
                "activeWANs": 0,
                "activeWiFiInterfaces": 0,
                "deviceCount": 0
            }

        serials = [ont['serial'] for ont in onts_to_query]
        logger.info(f"ONT serials to query: {serials}")
        
        pipeline = [
            {'$match': {'serial': {'$in': serials}}},
            {'$sort': {'timestamp': -1}},
            {'$group': {
                '_id': '$serial',
                'timestamp': {'$first': '$timestamp'},
                'totalBytesReceived': {'$first': {'$sum': '$wans.bytesReceived'}},
                'totalBytesSent': {'$first': {'$sum': '$wans.bytesSent'}},
                'activeWANs': {'$first': {'$size': {
                    '$filter': {
                        'input': '$wans',
                        'as': 'wan',
                        'cond': {'$eq': ['$$wan.connectionStatus', 'Connected']}
                    }
                }}},
                'totalWifiBytesReceived': {'$first': {'$sum': '$wifi.totalBytesReceived'}},
                'totalWifiBytesSent': {'$first': {'$sum': '$wifi.totalBytesSent'}},
                'activeWiFiInterfaces': {'$first': {'$size': {
                    '$filter': {
                        'input': '$wifi',
                        'as': 'wifi',
                        'cond': {'$eq': ['$$wifi.status', 'Up']}
                    }
                }}},
                'connectedHosts': {'$first': {'$size': '$hosts'}},
                'failedConnections': {'$first': {'$size': {
                    '$filter': {
                        'input': '$hosts',
                        'as': 'host',
                        'cond': {'$eq': ['$$host.active', False]}
                    }}
                }},
                'transceiverTemperature': {'$first': '$gpon.transceiverTemperature'},
                'rxPower': {'$first': '$gpon.rxPower'},
                'txPower': {'$first': '$gpon.txPower'},
            }},
            {'$group': {
                '_id': None,
                'timestamp': {'$max': '$timestamp'},
                'totalBytesReceived': {'$sum': '$totalBytesReceived'},
                'totalBytesSent': {'$sum': '$totalBytesSent'},
                'activeWANs': {'$sum': '$activeWANs'},
                'totalWifiBytesReceived': {'$sum': '$totalWifiBytesReceived'},
                'totalWifiBytesSent': {'$sum': '$totalWifiBytesSent'},
                'activeWiFiInterfaces': {'$sum': '$activeWiFiInterfaces'},
                'connectedHosts': {'$sum': '$connectedHosts'},
                'failedConnections': {'$sum': '$failedConnections'},
                'deviceCount': {'$sum': 1},
                'avgTransceiverTemperature': {'$avg': '$transceiverTemperature'},
                'avgRxPower': {'$avg': '$rxPower'},
                'avgTxPower': {'$avg': '$txPower'},
            }}
        ]
        logger.info(f"Executing MongoDB aggregation pipeline: {pipeline}")
        result = list(monitoring_data_collection.aggregate(pipeline))
        logger.info(f"Aggregation result: {result}")

        if not result:
            logger.warning("No results found from aggregation")
            return {
                "timestamp": None,
                "totalBytesReceived": 0,
                "totalBytesSent": 0,
                "totalWifiAssociations": 0,
                "activeWANs": 0,
                "activeWiFiInterfaces": 0,
                "deviceCount": 0
            }

        latest_values = result[0]
        latest_values['_id'] = building or floor or serial or "all"
        logger.info(f"Returning latest values: {latest_values}")
        return latest_values
     


    # Monitoring Configurations
    @staticmethod
    def get_monitoring_config():
        config_data = monitoring_config_collection.find_one()
        if config_data:
            return MonitoringConfig(**config_data)
        return MonitoringConfig()

    @staticmethod
    def update_monitoring_config(config: MonitoringConfig):
        monitoring_config_collection.update_one({}, {"$set": config.dict()}, upsert=True)