# launch_data_classes.py

class Manufacturer:
    def __init__(self, id, name, description, logoUrl, countryCode):
        self.id = id
        self.name = name
        self.description = description
        self.logoUrl = logoUrl
        self.countryCode = countryCode


class Rocket:
    def __init__(self, id, name, variant, description, length, diameter, launchMass, maxStage, thrust,
                 leoCapacity, gtoCapacity, totalLaunchCount, successfulLaunches, manufacturerId):
        self.id = id
        self.name = name
        self.variant = variant
        self.description = description
        self.length = length
        self.diameter = diameter
        self.launchMass = launchMass
        self.maxStage = maxStage
        self.thrust = thrust
        self.leoCapacity = leoCapacity
        self.gtoCapacity = gtoCapacity
        self.totalLaunchCount = totalLaunchCount
        self.successfulLaunches = successfulLaunches
        self.manufacturerId = manufacturerId


class Launch:
    def __init__(self, id, rocketId, missionName, missionDescription, padName, padLocation, missionOrbitAbv,
                 missionOrbit, status, webcastLive, launchWindowStart, launchWindowEnd, launchImageUrl,
                 agencies, netTime, padDescription, missionType, webStream, serviceProvider):
        self.id = id
        self.rocketId = rocketId
        self.missionName = missionName
        self.missionDescription = missionDescription
        self.padName = padName
        self.padLocation = padLocation
        self.missionOrbitAbv = missionOrbitAbv
        self.missionOrbit = missionOrbit
        self.status = status
        self.webcastLive = webcastLive
        self.launchWindowStart = launchWindowStart
        self.launchWindowEnd = launchWindowEnd
        self.launchImageUrl = launchImageUrl
        self.agencies = agencies  
        self.netTime = netTime  
        self.padDescription = padDescription  
        self.missionType = missionType  
        self.webStream = webStream 
        self.serviceProvider = serviceProvider  
