# HashCode_Geofence_BabyYodas

### Problem Statement Number 
PS4 Geofence

### Problem
We aim to create a boundary within which we can monitor any device. Once this boundary is set up, the
product/app can setup triggers, which can send a notification when an entity enters (or exits) the fence.
Geofencing enables the creation of unique user experiences that are specific to the context of the
location.
<br>

### Proposed Solution
For a centralized solution, we intend to offer the master node with selection of an origin (in terms of
latitude, longitude) and radius of the fence. Once this is created, any device entering the area within the
fence will be shown in the central dashboard and can be monitored. All the known devices will be
periodically checked for their position to monitor if they are in/out of the fence.
For the decentralized solution, we consider the convex hull of all the distributed masters.

### Working Principle
The geofence will be set around a particular master node at a pre fixed radius.
The devices around the fence will expose their positions at any instant (latitude,
longitude). If the device falls within the defined perimeter, we will be able to
monitor the device.

We can extend the solution to form a series of masters. Using similar logic as
above, if a device enters the convex hull of the decentralized masters, we will be
able to monitor it.
