# Meshwell
A gamer matchmaking system, developed using Python on the Django framework.

## Reason for creation
In the final year of my university degree, we were tasked with creating a product from inception to completion in the space of 12 weeks. As a team, we decided to create a matchmaking service which connects computer gamers together based on their preferences. The idea for this came about because some of the team members mused over how it was becoming difficult to find a time where their friends were free to play games, but still wanted to play with people when they were able to. Thus, we decided to create a service where players could specify their desired gaming timeslots and queue for a team whilst they were at uni or working etc. and receive a message when it was found. Since other players should match their desired qualities in a teammate, this would optimally lead to less wasted time trying to organise for other people to get on, and hopefully new friends to play games with.

## Method
1. Users create an account, then enter their desired playstyle, teammate preferences, and time availability.
2. Next, they link up their Discord and in-game accounts, using which Meshwell retrieves their match history and approximate rank. 
3. Using this information, Meshwell can match people together based on approximate skill level alone, much like online games already do. What makes it special however, is that Meshwell also creates teams based on commendations internally. 
4. Commendations act as a method for players to rate their teammates in a way that has an impact on who they will be matched with in future. This allows users to apply weighting to their desired attributes in a teammate when they begin searching for a session. 
5. When performing a search, Meshwell applies these weights to each applicant for a team alongside the other potential members to decide which team members would have the optimal synergy. 
6. Once the team has been formed, players are sent an email with the timeslot that they have been allocated, as well as a link to a Discord channel 10 minutes before their timeslot occurs. 
7. The Discord channel is created using a bot which scans the database once per minute and channel entry is restricted to those who are involved in the session. 
8. When the session completes, the channel remains open for 10 minutes (after which it is deleted automatically) and players are sent an invitation to grade their teammates based on the qualities they have shown. 
9. Players can then search for a new session.  

### Commendations
Players have the ability to commend based on Teamwork, Positivity, Skill, and Communication. Players can also place weightings (importance) on each of thses commendations to skew the type of teammates they will be matched with.  

### API
Meshwell has a private REST API which third-parties can use to obtain a glimpse into the playstyles of users (once given permission).

## Tech used
- Django
- Django-REST MVC/MTV API
- Python
- HTML/CSS/JS
- MySQL
- VS Code

## Definition of done
This project will be defined as completed when:
- [x] Players can create an account which is linked to their discord and in-game accounts.
- [x] Players can queue for a session and be matched with other players.
- [x] Players can place weightings on their desired qualities in a teammate and have matches take those into consideration.
- [x] Players can rate their teammates after a session has completed.
- [x] Players can provide feedback on their experience with Meshwell.
- [x] Administrators can help to moderate the userbase through an administration panel.
- [x] An API exists to obtain information about the playerbase.

### Stretch goals
There are a number of stretch goals which we would like to implement:
- [x] A discord bot which handles the creation of sessions and VoIP capability for Meshwell.
- [ ] Advanced ML for per-player calculations to see what types of players they usually rate highly and provide recommendations to users based on that.

## Retrospective
- Our team had half non-technical people which helped ensure our documentation was above average.
- It's hard to point Scrum fortnightly sprint tasks if people have very flexible/changing availabilities on a per week basis.
- UI design and UX is very subjective, but can be quite enjoyable.
- In a university environment, everyones priorities are different and the project workload each team member takes on is not always equal.
- No recourse or mediation was provided by the university when team members could not reach an agreement. Although this is supposed to imitate a real project, it does not since there is nothing on the line for those who do not contribute as much as the rest of the group since they neither receive remuneration or a penalty at the end of the unit.
- There is a lot less documentation available for Django than React.
- The skills and tech used in this project got me around a lot of the concepts of full stack development.