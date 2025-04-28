from datetime import datetime, timedelta, timezone
import requests
from launchDataClass import Manufacturer, Rocket, Launch  
from dbSetup import createDb, insertIntoDb, clearDb


def getData():
    launchBaseUrl = 'https://ll.thespacedevs.com/2.3.0/launches/'

    # Time frame
    now = datetime.now()
    away = now + timedelta(days=14)

    # Adding the time frame to the filters
    netFilters = f'net__gte={now.isoformat()}&net__lte={away.isoformat()}'
    orbitalFilter = 'include_suborbital=false'
    filters = '&'.join((netFilters, orbitalFilter))
    mode = 'mode=normal'
    limit = 'limit=2'
    ordering = 'ordering=net'
    queryUrl = launchBaseUrl + '?' + '&'.join((filters, mode, limit, ordering))
    print(f'query URL: {queryUrl}')

    def getResults(queryUrl: str) -> dict or None:
        try:
            results = requests.get(queryUrl)
        except Exception as e:
            print(f'Exception: {e}')
        else:
            if results.status_code != 200:
                print(results.status_code)
                throttle_response = requests.get("https://ll.thespacedevs.com/2.3.0/api-throttle/")
                if throttle_response.status_code == 200:
                    throttle_data = throttle_response.json()
                    print(throttle_data)
                    print(f"Throttle Limit: {throttle_data.get('your_request_limit')}")
                    print(f"Remaining: {throttle_data.get('your_request_limit') - throttle_data.get('current_use')}")
                    print(f"Resets in: {throttle_data.get('next_use_secs')} seconds")
                return
            return results.json()

    # Perform first query
    results = getResults(queryUrl)

    if not results:
        return

    nextUrl = results['next']
    while nextUrl:
        nextResults = getResults(nextUrl)
        if not nextResults:
            return
        results['results'] += nextResults['results']
        nextUrl = nextResults['next']
    createDb()
    clearDb()
    # Loop through each launch and gather data
    for launch in results['results']:
        rocketId = launch['rocket']['configuration']['id']
        rocketName = launch['rocket']['configuration'].get('name')
        rocketVariant = launch['rocket']['configuration'].get('variant')
        missionName = launch['mission']['name']
        missionDescription = launch['mission']['description']
        padName = launch['pad']['name']
        padLocation = launch['pad']['location']['name']
        missionOrbitAbv = launch['mission']['orbit']['abbrev']
        missionOrbit = launch['mission']['orbit']['name']
        status = launch['status']['name']
        agenciesList = launch['mission'].get('agencies', [])
        agencies = agenciesList[0].get('name') if agenciesList else None
        padDescription = launch['pad']['description']
        missionType = launch['mission']['type']
        launchWindowStart = launch['window_start']
        netTime = launch['net']
        launchWindowEnd = launch['window_end']
        webcastLive = launch['webcast_live']
        launchId = launch['id']
        launchImageBase = launch['image']['thumbnail_url']
        webStreamList = launch.get('vid_urls', [])
        webStream = webStreamList[0] if webStreamList else None
        serviceProvider = launch['launch_service_provider']['name']

        
        rocketInfo = requests.get(f'https://ll.thespacedevs.com/2.2.0/config/launcher/{rocketId}')
        rocketData = rocketInfo.json()

        rocketDescription = rocketData.get('description')
        rocketLength = rocketData.get('length')
        rocketDiameter = rocketData.get('diameter')
        rocketMass = rocketData.get('launch_mass')
        rocketStages = rocketData.get('max_stage')
        rocketThrust = rocketData.get('thrust')
        rocketLeoCapacity = rocketData.get('leo_capacity')
        rocketGtoCapacity = rocketData.get('gto_capacity')
        totalFlights = rocketData.get('total_launch_count')
        successfulFlights = rocketData.get('successful_launches')

        manufacturerName = rocketData['manufacturer'].get('name')
        manufacturerDescription = rocketData['manufacturer'].get('description')
        manufacturerLogo = rocketData['manufacturer'].get('logo_url')
        manufacturerCountry = rocketData['manufacturer'].get('country_code')
        manufacturerId = rocketData['manufacturer']['id']
        
        # launchWindowStartFormatted = datetime.fromisoformat(launchWindowStart.replace("Z", "+00:00")).strftime('%Y-%m-%d %H:%M:%S %Z')
        # launchWindowEndFormatted = datetime.fromisoformat(launchWindowEnd.replace("Z", "+00:00")).strftime('%Y-%m-%d %H:%M:%S %Z')
        # netTimeFormatted = datetime.fromisoformat(netTime.replace("Z", "+00:00"))


        manufacturer = Manufacturer(
            id=manufacturerId,
            name=manufacturerName,
            description=manufacturerDescription,
            logoUrl=manufacturerLogo,
            countryCode=manufacturerCountry
        )

        rocket = Rocket(
            id=rocketId,
            name=rocketName,
            variant=rocketVariant,
            description=rocketDescription,
            length=rocketLength,
            diameter=rocketDiameter,
            launchMass=rocketMass,
            maxStage=rocketStages,
            thrust=rocketThrust,
            leoCapacity=rocketLeoCapacity,
            gtoCapacity=rocketGtoCapacity,
            totalLaunchCount=totalFlights,
            successfulLaunches=successfulFlights,
            manufacturerId=manufacturerId
        )

        launchObj = Launch(
            id=launchId,
            rocketId=rocketId,
            missionName=missionName,
            missionDescription=missionDescription,
            padName=padName,
            padLocation=padLocation,
            missionOrbitAbv=missionOrbitAbv,
            missionOrbit=missionOrbit,
            status=status,
            webcastLive=webcastLive,
            launchWindowStart=launchWindowStart,
            launchWindowEnd=launchWindowEnd,
            launchImageUrl=launchImageBase,
            agencies=agencies,  
            netTime=netTime, 
            padDescription=padDescription, 
            missionType=missionType,  
            webStream=webStream, 
            serviceProvider=serviceProvider  
        )

        insertIntoDb(manufacturer, rocket, launchObj)
        print(f'Inserted Launch {launchObj.id} into database.')



