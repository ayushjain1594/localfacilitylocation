# Local Facility Location
A case study for exploring capacity expansion options for a fulfillment style distribution system with limited geographic scope.


## Background
This case study explores different options for expanding capacity to fulfill increasing customer demands in terms of fulfillment centers. As the name suggests, the geograpghic scope of this study is limited such as a major city or greater city regions.

**Information at hand:**
1. Customers:
	* 7000 customers
	* Geolocation for each
	* Average number of shipments per day by year for next five years

2. Sites:
	* 3 fulfillment centers
	* Geolocation for each
	* 20000 shipments per day capacity of each


**Potential Solutions:**
| Capacity Expansion At Existing Sites | Addition of One New Fulfillment Center |
|--------------------------------------|----------------------------------------|
|Expand capacity in terms of shipments per day for some or all the existing fulfillment centers|Open a new fulfilment center in the area starting 2021|
|Assumes exapanding existing sites is possible|Assumes that no existing site can be expanded
|Potentially (and relatively) inexpensive choice|Potentially expensive choice
|Difficult to improve upon current service levels| Potential to improve upon current service levels and shipping costs|
 
## Assumptions and Approach
**Network Flow Optimization**
The primary decision involve identifying average per day ‘flows’ of shipments from each FC to Customer. Most other decisions can be inferred from flows.

Model optimizes flows based on following costs structure – 

Fixed Cost = Distance in Miles (independent of number of shipments)
Variable Cost = 0.1 x Distance x Shipments

This can be interpreted as a delivery service charging a fixed cost based on distance and variable cost based on distance and shipment size.

**Consideration of routing:**
Due to the limited geographic scope of our network, we assume -
We are tackling the last mile of the supply chain.
Shipments are small items allowing several deliveries in one trip.
700 shipments capacity of truck.
Max route length equivalent to a ‘minimum spanning tree’ of 7 miles.

Due to computational complexity, we solve the entire problem in parts. 

We claim that reducing service distance under network optimization should indirectly reduce routing distance. We seek to support this claim from results.
