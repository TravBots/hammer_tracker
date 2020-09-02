### Setup
1. Clone the repository
2. Create a virtual environment
	- `pip3 -m venv env`
3. Install dependencies
	- `pip3 install -r requirements.txt`
4. Create the init file called `config.ini`
	- `default` header
	- `token` variable
	- `database` variable

#### Known Bugs
- If a multi-part IGN ends in a space followed by an integer (e.g. Player 1), the integer will be read the command specifying how many reports to return rather than part of the IGN. This can be circumvented by supplying a value for the number of reports to return (e.g. Player 1 1)

