# Recruitment-Agent

still under production ...
Directory Env Require:
1 folder name: Candidate to contain CV candidate from email
1 folder name: Pass to contain CV candidate who pass (this folder serve for human review)
1 file: joblist.txt - list job open. Ex: Ai Engineer Intern, Sale Executive Junior
each position have 1 folder: [position name], in that folder contain JD for that job and scoring_criteria.txt - contain list category to scoring candidate


---Candidate
|
---Pass
|
---joblist.txt
|
---Job_Title_1
|        |---JD.docx/.pdf
|        |---scoring_criteria.txt
|
---Job_Title_2
|
---Agent.ipynb
---tools.py


Although this folder structure is somewhat complex, it ensures that the agent accesses the correct context it needs, reducing the search load. The agent only needs to search by file name and access the exact job description for the job it wants.
