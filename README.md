# Agent Based Traffic Simulation



## Introduction

This is my graduate project for my Master's degree at Towson University. 


### Context
Modern traffic simulations often treat individual drivers and vehicles as a monolith, overlooking rich variation in driving styles that can lead to congestion. This project proposes an agent-based simulation that explicitly encodes different driving personalities to investigate how they shape localized traffic patterns. 


### Problem Statement
The lack of nuance given to traffic simulations causes inadequate road designs for proposed projects, leading to increases in vehicle-related problems such as traffic wait times, car crashes, and environmental impact, and these findings need to be quantified. 


## Approach
This project will implement a Java-based agent-oriented approach. Each vehicle will act as its own autonomous object and be given a “personality”. The personality profile will have various levels of acceleration aggressiveness, lane-change frequency, desired follow distance, risk tolerance, etc. Simulations will be created based on generated scenarios with adjustable traffic densities, road lanes, personality mixes, etc. Time series data will be recorded, and throughput, average speed, and other key indicators will be measured.  

## Topics Studied
1. Agent-based design- Understanding the different architectures, types of behaviors, how decisions are made, etc. 

2. Traffic simulation design- Learning the fundamentals of what is needed to create a traffic simulation, such as how to design roads and lane changes. 

3. Simulation Frameworks- The diverse ways to build a simulation and apply the learning to this project. 

4. Data collection design- How to set up logging of different states within the simulation, and how to store that information efficiently and in a way that aids quick analysis. 

5. Designing efficient programs - Given that simulations tend to be resource-intensive, any design change that can increase efficiency will help. 


## Project Objectives
1. Mastering traffic flow theory- Understand the fundamentals of traffic flow that are accepted by traffic engineers. 

2. Applying agent-based modeling techniques- Design autonomous driving agents who can simulate real-world drivers and model traffic dynamics. 

3. Utilize object-oriented design patterns- Build a maintainable and extendable Java codebase. 

4. Enhance data analysis proficiency-Transform raw data into meaningful plots and explanations using EDA, classification, regression, and/or clustering. 

5. Practice professional software development- utilize issue tracking and branching using GitHub. 

## Deliverables

| Status | Deliverable | Description |
|-|-|-|
|&#x2610; | Source Code Repository | Well-maintained java project hosted on GitHub |
|&#x2610;|Project Requirements Document |Detailed specification of functional requirements that should be achieved | 
|&#x2610;|Process Diagrams |Visual representation of key events and the flow of specific processes |
|&#x2610;|Class Diagrams |The attributes and functionality of each class created with this project |
|&#x2610;|Database Schema  |A relational diagram with tables, fields, constraints, key, foreign key, etc. |
|&#x2610;|Database Creation Script |Automatically generated script to create the database on a separate server, including both schema and data objects 
|&#x2610;|Simulation Executable |An executable to start the simulation, works in tandem with the database creation script |
|&#x2610;|Statistical Analysis Report |Report after analysis was performed on the resulting dataset. |
|&#x2610;|User Manual |An explanation of how to use the User Interface  |
|&#x2610;|Final Project Report |Comprehensive write-up that combines all aforementioned deliverables with discussion, backup methodology, results, future work, references, etc. |

