select database();

show tables;

create table if not exists users (
	id int auto_increment primary key,
    username varchar(255),
    password varchar(255),
    privilege varchar(255)
);

use university;
select * from users;

drop table users;
