# rasapp
Roster distribution flask app

run server.py, then enter to http://127.0.0.1:5000/

## Tutorial

You need to login the website.

Then:
You can addUser (as long as his id is not used already), editUser and removeUser.
![alt text](https://github.com/lanyado/rasapp/raw/master/general/images/user_actions.png "User actions")

A user has <exemptions>: <br>
An exemption is for <weekday> or <weekend>.<br>
An exemption is for a duty type (kitchen, gaurd).<br>
An exemption has an <expire date>, when the expire date has past, the exemption gets deleted.<br>

You can pick up dates from the calendar and create a <duties table>.<br>
As long as there are enugh <available workers>.
![alt text](https://github.com/lanyado/rasapp/raw/master/general/images/calendar.png "Calendar")

A user will become a worker if:
1. He's the user with the oldest <last_weekday> / <last_weekend>.
2. He doesn't have an exemption for that duty type on that time (exemple: kitchen on weekend).
3. His recent duty was two days before the new duty's date.

* A weekend is from Thoursday to Saturday, a worker on a weekend will be all along the weekend.
* If there are many users that can be workers (on that date and type), the system will choose one of them randomaly.

Then:
1. His info will be in the spesific cell of the duties table.
2. The duty's date will be set in his  <last_weekday> or <last_weekend>.
3. His <last_weekday> or <last_weekend> will be extend with `"duty date" : "duty type"`.
