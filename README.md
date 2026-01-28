# Proffquest
Proffquest is the web application to search jobs where verified company can advertise their vacant jobs and skilled users can apply for their role and company can hire them. The whole applicaton will handled by Admin where he can verify and blacklist companies as required.
# steps
1. create model for database, add relation[backref vs back_populates]
backref: can use in one model only like if we have relation btw admin and applications and we can use it in only one model for fetching admin.applications
back_populates: can use in both models for fetching
2. we add admin in different file(default_admin.py)
3. we setup jwt token for role based access

