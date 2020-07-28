# Local Facility Location
A case study for exploring capacity expansion options for a fulfillment style distribution system with limited geographic scope.


## Background
This case study explores different options for expanding capacity to fulfill increasing customer demands in terms of fulfillment centers. As the name suggests, the geograpghic scope of this study is limited such as a major city or greater city regions.

**Information at hand:**
1. Customers:
	* 7,000 customers
	* Geolocation for each
	* Average number of shipments per day by year for next five years

2. Sites:
	* 3 fulfillment centers
	* Geolocation for each
	* 20,000 shipments per day capacity of each

![Demand vs Capacity](/images/demand_vs_capacity.PNG)


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

 * Fixed Cost = Distance in Miles (independent of number of shipments)
 * Variable Cost = 0.1 x Distance x Shipments

This can be interpreted as a delivery service charging a fixed cost based on distance and variable cost based on distance and shipment size.

**Consideration of routing:**
Due to the limited geographic scope of network, the study assumes -

 * This is the last mile of the supply chain.
 * Shipments are small items allowing several deliveries in one trip.
 * 700 shipments capacity of truck.
 * Max route length equivalent to a ‘minimum spanning tree’ of 7 miles.

Due to computational complexity, the entire problem is solved in parts. 

It is claimed that reducing service distance under network optimization should indirectly reduce routing distance. The study seeks to support this claim from results.

**Process**

Flow Optimization:

 * Obtain avg per day network flows by year from FCs to Customers. 
 * This forms clusters of customers, each belonging to a fulfillment center.
 * This problem is solved as Mixed Integer Programming problem using Gurobi.

[Clusterization](https://github.com/ayushjain1594/quicluster):

 * Flows obtained show clusters of customers each FC serves in a year.
 * For each FC and its cluster, further sub-clusters are created using a modified Kruskal’s algorithm to create a forest of minimum spanning trees where each tree represents a sub-cluster.
 * Customers in a sub-cluster are to be delivered on the same truck.

[Routing](https://github.com/ayushjain1594/localsearchtsp):

* For each sub-cluster routes are created using 3OPT heuristic with additional node for FC where each tour begins and ends.

**Scenarios**

Scenarios are named based on elements that are added on top of baseline. Their timeline is shown below.

|2020|2021|2022|2023|2024|2025|
|----|----|----|----|----|----|
|S1  |	  |    |    |    |    |
|S3  |S3  |S3  |S3  |S3  |S3  |
|S4  |S4  |S4  |S4  |S4  |S4  |

S1 : Baseline

 * Only created for the period of 2020, infeasible in future years.
 * Model current network design, estimate current costs and service levels. 
 * Assumes that current design is optimal under the current cost structure.

S3 : Baseline + SlackCap + FutureYears

 * Extend baseline to include future years.
 * Allow additional 20,000 orders per day capacity (slack) for each site.
 * Note that the slack capacity is added beginning 2020 for two reason – comparison with baseline and peek at the ‘perfect world’ scenario by being able to compare with Baseline which exists only for 2020. 
 * Slack capacity is available at a small penalty in model however it is not accounted under ‘cost’ in results.

S4 : Baseline + NewSites + FutureYears

 * Extend baseline NO to include future years 
 * 10 candidates within Seattle for potentially max 1 new site starting 2021.
 * New Site to have 20,000 orders per day capacity, same as others.
 * No slack capacity for any site.

**Metrics and KPIs**
| Cost Based | Service Based |
|------------|---------------|
|Per day network flow cost|% Customers serviced by FC within 4 Miles|
|Per day routing miles|% Customers serviced by FC within 5 Miles|
|% Routes over 12 Miles| |

## Scenario Comparison

*Due to identical days within a year, numbers shown for a year are numbers on any day in that year.*

**Baseline vs S3 (2020)**

![Baseline vs S3](/images/S1_S3.png)

**S3 vs S4**

![S3 vs S4](/images/S3_S4.png)

## Takeaways

Comparing Baseline to S3 for year 2020, additional 3630 orders per day capacity has following immediate benefits:

 * 4.53% reduction in network flow cost.
 * 4.74% reduction in delivery miles.
 * 4% additional customers serviced by FC within 4 miles.
 * 6% additional customers serviced by FC within 5 miles.
 * 5% lesser routes over 12 miles.
 * No routes over 16 miles.


Comparing Scenario 3 (Baseline + SlackCap + FutureYears) to Scenario 4 (Baseline + NewSites + FutureYears), opening a new site over expanding capacity has following benefits:

 * 16.73% reduction in network flow cost.
 * 8.23% reduction in delivery miles.
 * 10% additional customers serviced by FC within 4 miles.
 * 4% lesser routes over 12 miles.
 * More balanced shipment volumes among FCs. 

As was claimed, the results show that reducing service distance indeed reduces routing miles, coming primarily from reduction in miles driven on first and final leg of routes.

Results support the approach and should be further explored in order to make well informed decision.