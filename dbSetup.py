import sqlite3
from launchDataClass import Manufacturer, Rocket, Launch

def createDb():
    conn = sqlite3.connect('launchData.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Manufacturer (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            logoUrl TEXT,
            countryCode TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Rocket (
            id INTEGER PRIMARY KEY,
            name TEXT,
            variant TEXT,
            description TEXT,
            length REAL,
            diameter REAL,
            launchMass REAL,
            maxStage INTEGER,
            thrust REAL,
            leoCapacity REAL,
            gtoCapacity REAL,
            totalLaunchCount INTEGER,
            successfulLaunches INTEGER,
            manufacturerId INTEGER,
            FOREIGN KEY (manufacturerId) REFERENCES Manufacturer (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Launch (
            id TEXT PRIMARY KEY,
            rocketId INTEGER,
            missionName TEXT,
            missionDescription TEXT,
            padName TEXT,
            padLocation TEXT,
            missionOrbitAbv TEXT,
            missionOrbit TEXT,
            status TEXT,
            webcastLive TEXT,
            launchWindowStart TEXT,
            launchWindowEnd TEXT,
            launchImageUrl TEXT,
            agencies TEXT,
            netTime TEXT,
            padDescription TEXT,
            missionType TEXT,
            webStream TEXT,
            serviceProvider TEXT,
            FOREIGN KEY (rocketId) REFERENCES Rocket (id)
        )
    ''')

    conn.commit()

    conn.close()

    # print("Database and tables created successfully.")

def insertIntoDb(manufacturer: Manufacturer, rocket: Rocket, launch: Launch):
    conn = sqlite3.connect('launchData.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO Manufacturer (id, name, description, logoUrl, countryCode)
        VALUES (?, ?, ?, ?, ?)
    ''', (manufacturer.id, manufacturer.name, manufacturer.description, manufacturer.logoUrl, manufacturer.countryCode))

    cursor.execute('''
        INSERT OR REPLACE INTO Rocket (id, name, variant, description, length, diameter, launchMass, maxStage, thrust,
        leoCapacity, gtoCapacity, totalLaunchCount, successfulLaunches, manufacturerId)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (rocket.id, rocket.name, rocket.variant, rocket.description, rocket.length, rocket.diameter, rocket.launchMass,
          rocket.maxStage, rocket.thrust, rocket.leoCapacity, rocket.gtoCapacity, rocket.totalLaunchCount,
          rocket.successfulLaunches, rocket.manufacturerId))

    cursor.execute('''
        INSERT OR REPLACE INTO Launch (id, rocketId, missionName, missionDescription, padName, padLocation,
        missionOrbitAbv, missionOrbit, status, webcastLive, launchWindowStart, launchWindowEnd, launchImageUrl,
        agencies, netTime, padDescription, missionType, webStream, serviceProvider)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (launch.id, launch.rocketId, launch.missionName, launch.missionDescription, launch.padName,
          launch.padLocation, launch.missionOrbitAbv, launch.missionOrbit, launch.status, str(launch.webcastLive).lower(),
          launch.launchWindowStart, launch.launchWindowEnd, launch.launchImageUrl, launch.agencies,
          launch.netTime, launch.padDescription, launch.missionType, str(launch.webStream).lower(),
          launch.serviceProvider))

    conn.commit()
    conn.close()

import sqlite3

def clearDb():
    try:
        conn = sqlite3.connect("launchData.db")
        cursor = conn.cursor()
        tables = ['Launch', 'Rocket', 'Manufacturer']

        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        
        conn.commit()
        # print("Database cleared successfully.")

    except sqlite3.Error as e:
        print(f"Error unable to delete Data: {e}")
    finally:
        conn.close()
