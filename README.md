# rasapp
Roster distribution flask app

run server.py, then enter to http://127.0.0.1:5000/

## Tutorial

You need to login the website.

Then:
You can addUser (as long as his id is not used already), editUser and removeUser.
![alt text](https://github.com/lanyado/rasapp/raw/master/general/images/user_actions.png "user actions")

A user has <b>exemptions</b>:<br>
An exemption is for <b>weekday</b> or <b>weekend</b>.<br>
An exemption is for a duty type (kitchen, gaurd).<br>
An exemption has an <b>expire date</b>, when the expire date has past, the exemption gets deleted.<br>
<img alt='exemptions' src="https://github.com/lanyado/rasapp/raw/master/general/images/exemptions.png" data-canonical-src="https://github.com/lanyado/rasapp/raw/master/general/images/exemptions.png" width="350" height="400" />

You can pick up dates from the calendar and create a <b>duties table</b>.<br>
As long as there are enugh <b>available workers</b>.
![alt text](https://github.com/lanyado/rasapp/raw/master/general/images/calendar.png "calendar")

A user will become a worker if:
1. He's the user with the oldest <b>last_weekday</b> / <b>last_weekend</b>.
2. He doesn't have an exemption for that duty type on that time (exemple: kitchen on weekend).
3. His recent duty was two days before the new duty's date.

* A weekend is from Thoursday to Saturday, a worker on a weekend will be all along the weekend.
* If there are many users that can be workers (on that date and type), the system will choose one of them randomaly.

Then:
1. His info will be in the spesific cell of the duties table.
2. The duty's date will be set in his  <b>last_weekday</b> or <b>last_weekend</b>.
3. His <b>last_weekday</b> or <b>last_weekend</b> will be extend with `"duty date" : "duty type"`.

![alt text](https://github.com/lanyado/rasapp/raw/master/general/images/duties_table.png "user actions")