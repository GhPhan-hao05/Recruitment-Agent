# Recruitment-Agent

still under production ...<br>
**Directory Env Require:**<br>
1 folder name: **Candidate** to contain CV candidate from email<br>
1 folder name: **Pass** to contain CV candidate who pass (this folder serve for human review)<br>
1 file: **joblist.txt** - list job open. Ex: Ai Engineer Intern, Sale Executive Junior<br>
n position have n folder: **Job_Title_**, in that folder contain **JD.docx/.pdf** for that job and **scoring_criteria.txt** - contain list category to scoring candidate<br>


---Candidate<br>
|<br>
---Pass<br>
|<br>
---joblist.txt<br>
|<br>
---Job_Title_1<br>
|        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|---JD.docx/.pdf<br>
|        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|---scoring_criteria.txt<br>
|<br>
---Job_Title_2<br>
|<br>
---Agent.ipynb<br>
---tools.py<br>


Although this folder structure is somewhat complex, it ensures that the agent accesses the correct context it needs, reducing the search load. The agent only needs to search by file name and access the exact job description for the job it wants.
