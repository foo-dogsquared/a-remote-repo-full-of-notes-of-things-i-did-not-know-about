# Relational databases
You might've encountered a situation wherein you have to represent your data with a table whether it's through spreadsheets or with good 'ol plain paper. The most common example with this is when we go through our budget or listing out people within a class or an office. 

With those data, we often just list out our expenses or individual people in the list and write out their related data.

| Description | Cost 
| --- | --- |
| Electricity | ₱1200.00
| Food | ₱1000.00
| Project expenses | ₱950.00
| Transportation | ₱750.00

Relational databases are a type of database that uses one or more tables composed of columns and rows to represent their data. 

Each row represents one individual data that can be called as a *record*. Each record should contain a unique key (mostly referred to as the *primary key*) to easily find, identify, and refer to the data. Consider a database for a video game store wherein certain games can be sold for renting. In order to uniquely identify them and not cause some headache in cases that they have the same name (or the like), we assign a unique ID for the individual items.

| Unique ID | Game title | 
| --- | --- |
| 1 | Your Very Ordinary RPG
| 2 | Your Very Ordinary RPG 2
| 3 | Sanic & Kunuckles & Towels & Knuckles *Featuring Dante from the Devil May Cry series*
| 4 | Dogs & Cats: The Movie: The Video Game
| 5 | Hitching and Ditching
| 6 | Alive Island
| 7 | First Reality: The First One
| 8 | First Reality: The 50th One
| 9 | First Reality: The Hundreth Spin-Off
| 10 | Capsule Monsters
| 11 | First of Them
| 12 | Celestial Souls
| 13 | Celestial Souls II
| 14 | Celestial Souls III
| 15 | Mahvel VS PopCom 3: Fate of Two Whales *Featuring Dante from the Devil May Cry series*
| 16 | Mahvel VS PopCom 3: Fate of Two Whales ULTRA
| 42 | Deviant Hunter: Freedom Union
| 43 | Deviant Hunter: Freedom Union 2G
| 44 | Deviant Hunter: Freedom Union 3G

The column represents one of the *attributes* that describes a part of each record. In the same example, we could take the video game store with the list of games that can be rented and create a table where each game is listed with its title, developer, published year, and the information of the person who rented them along with the due date.

| Unique ID | Game title | Developers | Published Year | Customer | Duration | Due Date
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Your Very Ordinary RPG | Cube Enix | 2014 | N/A | N/A | N/A
| 2 | Your Very Ordinary RPG 2 | Cube Enix | 2014 | N/A | N/A | N/A
| 3 | Sanic & Kunuckles & Towels & Knuckles *Featuring Dante from the Devil May Cry series* | Segway | 2019 | Gabe Newell | 14 days | 2018/02/14
| 4 | Dogs & Cats: The Movie: The Video Game | Distortion Games | 1999 | N/A | N/A | N/A
| 5 | Hitching and Ditching | N/A | N/A | N/A | N/A | N/A
| 6 | Alive Island | Shallow Gold | 2005 | John Doe | 7 days | 2018/02/07
| 7 | First Reality: The First One | Cube Enix | 2000 | John Doe | 7 days | 2018/02/07
| 8 | First Reality: The 50th One | Cube Enix | 2015 | John Doe | 7 days | 2018/02/07
| 9 | First Reality: The Hundredth Spin-off | Cube Enix | 2018 | John Doe | 7 days | 2018/02/07
| 10 | Capsule Monsters | Nincompo | 1998 | N/A | N/A | N/A
| 11 | First of Them | Kind Cat | 2013 | Joshua Dimmer | 1 day | 2018/01/31
| 12 | Celestial Souls | id Object | 2008 | N/A | N/A | N/A
| 13 | Celestial Souls II | id Object | 2013 | N/A | N/A | N/A
| 14 | Celestial Souls III | id Object | 2017 | N/A | N/A | N/A
| 15 | Mahvel VS PopCom 3: Fate of Two Whales *Featuring Dante from the Devil May Cry series* | Popcom | 2013 | Minimum Dudette | 14 days | 2018/02/14
| 16 | Mahvel VS PopCom 3: Fate of Two Whales ULTRA | Popcom | 2014 | N/A | N/A | N/A
| 42 | Deviant Hunter: Freedom Union | Popcom | 2010 | N/A | N/A | N/A
| 43 | Deviant Hunter: Freedom Union 2G | Popcom | 2011 | Poc Orc | 30 days | 2018/03/02
| 44 | Deviant Hunter: Freedom Union 3G | Popcom | 2012 | Poc Orc | 30 days | 2018/03/02

Well, there we have it. It's a simple database but there are problems that'll pop up. First, obviously there are cases wherein one customer can rent multiple games (unless you've enforced a policy that lets them to have only one game to rent for some reason) and we could just put the customer information in each of the games that they rented but that's too tedious and prone to errors. But the most obvious of them all is that this database seems hard to maintain, it requires you to input the customers data multiple times and that could go a long way to problem city.

One of the solutions for that is we could just make another database with it and *relate* it (see where's the name going from) with the other databases when needed. This is known as *normalization* which is basically the process of dividing our data into places, getting rid of repetitive information, and making our data to be efficient. 

The benefits that could get from normalizing our tables could be the following:

- Reducing the need to repeatedly input our data
- Furthermore, it also makes it less prone to manual input error
- Decrease storage space

In this case, we could separate the whole renting games database into three databases: 

- the customers who rent
- the game available for renting
- the transactions for renting

Creating the first two databases simply means we just separate them and give each piece a unique key.

We assigned each customer a unique key. It also reduces the need to repeatedly enter their data since they could rent multiple games in one transaction (which is one of the potential problems that was addressed earlier).

| Customer ID | First Name | Last Name
| --- | --- | --- |
| 2 | Gabe | Newell
| 42 | Grace | Hopper
| 301 | John | Doe
| 612 | Wyatt | Moss
| 750 | Joshua | Dimmer
| 1002 | Pop | Orc
| 137560 | Minimum | Dudette

Same with the games. We assigned a primary key for the games which is represented by an integer:

| Unique ID | Game title | Developers | Published Year 
| --- | --- | --- | --- |
| 1 | Your Very Ordinary RPG | Cube Enix | 2014 
| 2 | Your Very Ordinary RPG 2 | Cube Enix | 2014 
| 3 | Sanic & Kunuckles & Towels & Knuckles *Featuring Dante from the Devil May Cry series* | Segway | 2019 | 
| 4 | Dogs & Cats: The Movie: The Video Game | Distortion Games | 1999 
| 5 | Hitching and Ditching | N/A | N/A
| 6 | Alive Island | Shallow Gold | 2005
| 7 | First Reality: The First One | Cube Enix | 2000
| 8 | First Reality: The 50th One | Cube Enix | 2015
| 9 | First Reality: The Hundredth Spin-off | Cube Enix | 2018
| 10 | Capsule Monsters | Nincompo | 1998
| 11 | First of Them | Kind Cat | 2013 
| 12 | Celestial Souls | id Object | 2008
| 13 | Celestial Souls II | id Object | 2013
| 14 | Celestial Souls III | id Object | 2017
| 15 | Mahvel VS PopCom 3: Fate of Two Whales *Featuring Dante from the Devil May Cry series* | Popcom | 2013 
| 16 | Mahvel VS PopCom 3: Fate of Two Whales ULTRA | Popcom | 2014
| 42 | Deviant Hunter: Freedom Union | Popcom | 2010
| 43 | Deviant Hunter: Freedom Union 2G | Popcom | 2011
| 44 | Deviant Hunter: Freedom Union 3G | Popcom | 2012 

After that, we could create the last table. The "RENT" table contains the name of the game and the customer who is currently renting it. We already have tables for the available games and the customers and we already assigned primary keys for them so we will just use those. Of course, we would also assign a primary key for each of the transactions.

| Transaction ID | Game ID | Customer ID | Duration | Due Date
| --- | --- | --- | --- | --- |
| 1 | 3 | 2 | 14 days | 2018-02-14
| 2 | 6 | 301 | 7 days | 2018-02-07
| 3 | 7 | 301 | 7 days | 2018-02-07
| 4 | 8 | 301 | 7 days | 2018-02-07
| 5 | 9 | 301 | 7 days | 2018-02-07
| 6 | 11 | 750 | 1 day | 2018-01-31
| 7 | 15 | 137560 | 14 days | 2018-02-14
| 8 | 43 | 1002 | 30 days | 2018-03-02
| 9 | 44 | 1002 | 30 days | 2018-03-02

With normalizing databases, we also declare a relationship between data and how do they relate with one another. This is where the *relation* in relational databases takes place. The result from the normalization of the previous example now has three databases but only one of them is dependent which is the the `RENT` table which needs the `GAMES`'s and the `CUSTOMER`'s ID.

In these cases, we would call the `RENT` table the *child* and the `GAME` and `CUSTOMER` table to be the *parent*. One classic way of identifying the parent table and the child table is looking for the field which refers to the other table's primary key/ID which we just did.

Another way of identifying it is thinking about which table could contain a record without needing for a reference from the other table. 

From the `GAME` and the `RENT` table, can we have a game that has never rented yet? The answer is yes. Now let's ask the other way around. Can we have a rent transaction that refers to a non-existent game? The answer is generally no. Hence, the child table is the `RENT` table and the parent table is the `GAME`. The same principle can be applied between the `CUSTOMER` and the `RENT` table. Try it as an exercise.

Now that we have discussed a bit on the concepts of relational databases, you might gain an idea of what a relational database is. **It's a data model that uses one or more tables and relating data from one table to another.**

In the example, you can see that we have three tables and one of the tables utilizes data from the other two. That particular table relates data from the `GAME` table and the `CUSTOMER` table.

<img alt="Tables' relationship in the example" style="display: block; margin: 0 auto;" src="data:image/png;base64,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">

There are more than

First, you have to set a pre-defined schema. In other words, it requires a bit of planning before you can get to fully use it. If you find yourself to normalize or de-normalize your table, you're going under a messy process trying to migrate the data that is needed to be migrated. Furthermore, you can't just add another attribute into your table when it needs to. All of the records inside of a table must be covered with all of the attributes of the table.

Second is the data integrity or consistency. With relational databases that is composed of multiple tables, surely some of them are made up of cross-referential data with other tables. In cases such as the referred data has changed, you also have to make sure that the tables involved have their records reflect the occured changes and nothing broke out of that. The prominent example for that is when the referred record has been deleted, you have to make sure that the tables in the database involved with the record has deleted the rows that referred to that record.

Relational databases usually go hand-in-hand with SQL, a query language that describes the implementation of data interaction in a relational database. In order to use it, you would need to download a DBMS that utilizes the language such as [MySQL](https://www.mysql.com/), [Microsoft SQL Server](https://www.microsoft.com/en-us/sql-server), [Oracle Database](https://oracle.com/database), and [PostgreSQL](https://postgresql.org/). Mind you that while they use SQL syntax, there are some subtle difference between each of them. They might even include some exclusive syntax which is not present in other SQL-based DBMS. 

Overall, what SQL provides is a solid language that is similar to English sentences. 

Let's put that to the test. Assuming you have no experience with using SQL yet, can you tell what these SQL statements indicate?

```SQL
CREATE TABLE GAMES(
    PRIMARY KEY INTEGER game_id
    TEXT title
    TEXT developer
    INTEGER published_year
);

SELECT * FROM GAMES;

INSERT INTO GAMES(title, developer, published_year) VALUES ("Mahvel VS PopCom: Infinite", "PopCom", 2020);

SELECT * FROM GAMES WHERE published_year < 2010;
```

## Non-relational databases and NoSQL
Ever since SQL-based DBMS and SQL was booming in popularity way back in 1990s (as far as my research goes), several alternatives have been devised for various reasons and that's where NoSQL comes in.

NoSQL (stands for Not Only SQL) is a query language that try to use non-relational databases as their data model. NoSQL aims to provide an alternative way for data handling that relational databases usually have difficulties with. Examples such as  
