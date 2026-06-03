OpenHands Assignment
Overview:
Assignment is driven by spec driven development and TDD.
We will be using superpowers plugin to generate standard spec templates and TDD workflows. 

Phase 0: Setup
1. Setup github repository
2. Create claude base repositories. 
3. Initialize git in the project and push to the remote. 

Phase 1: Tic-Tac-Toe app
1. Generate spec for tic-tac-toe app
2. Break the spec into executable tasks. 
3. Interate through each task and implement it. For the sake of assignment - we will be grouping the tasks and implementing them in bulk with claude code. The implementation will follow TDD
4. Generate ci to make sure it is green before further code pushes to github
5. Generate a taskfile.yaml for local testing
6. Test locally with taskfile before pushing to github. Helps clear issues before ci catches them 


Things that are skipped intentionally: 
1. multiple branches for each task and PRs
2. running local taskfile to validate tests and checks after each task
3. Push to git after each task
