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

| Deliverable | Description |
|-|-|
| Source Code Repository | Well-maintained java project hosted on GitHub |
|Project Requirements Document |Detailed specification of functional requirements that should be achieved | 
|Process Diagrams |Visual representation of key events and the flow of specific processes |
|Class Diagrams |The attributes and functionality of each class created with this project |
|Database Schema  |A relational diagram with tables, fields, constraints, key, foreign key, etc. |
|Database Creation Script |Automatically generated script to create the database on a separate server, including both schema and data objects 
|Simulation Executable |An executable to start the simulation, works in tandem with the database creation script |
|Statistical Analysis Report |Report after analysis was performed on the resulting dataset. |
|User Manual |An explanation of how to use the User Interface  |
|Final Project Report |Comprehensive write-up that combines all aforementioned deliverables with discussion, backup methodology, results, future work, references, etc. |






To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/justakline/agent-based-traffic-simulation.git
git branch -M main
git push -uf origin main
```