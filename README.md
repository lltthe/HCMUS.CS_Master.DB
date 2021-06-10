# About the project

- This implementation serves the final project of Advanced Databases course - HCMUS Master K30 class, Term 1.
- A system that demonstrates The Coffee House business that is able to interact with 4 DB types:
  - Relational - MySQL
  - Graph - Neo4j
  - Document - MongoDB
  - Key-value - Memurai-Redis
- Written in Python and tested on Windows.
- May 2021.

## Owners

**Group 07:**
| Member | Student ID |
| - | - |
| Võ Đăng Khoa | 20C11008 |
| Nguyễn Đình Khải | 20C11032 |
| Lâm Lê Thanh Thế | 20C11053 |

## Contacts

- :email: Email:
  - lamlethanhthe@gmail.com
  - 20c11053@student.hcmus.edu.vn

## Other notes

- Theoretical details are in the report and presentation slides delivered together with this implementation.
- This is **NOT** intendedly supposed to be **PUBLIC**.
- *IMPORTANT:* Please **AVOID** using 'ĐALT' **(Unicode chars) in any path** when coding/deploying as it may cause problems.

# How to deploy/run

- Check the `requirements.txt` for packages needed to recreate a virtual environment.
- Run `main.py`, first connect to the 5 DBMS as prompted.
  - Make sure to install 4 DMBS [listed above](#about-the-project).
  - You can fill your usernames and passwords to `db_credentials.json` for easier and automatic logins.
- Open client windows and start interacting.