-- Keep a log of any SQL queries you execute as you solve the mystery.

--Considering there is a table named bakery_security_logs could be that the crime happened near a bakery
select * from crime_scene_reports where description like '%bakery%';
-- answer: 2021 | 7     | 28  | Humphrey Street | Theft of the CS50 duck took place at 10:15am at the Humphrey Street bakery. Interviews were conducted today with three witnesses who were present at the time – each of their interview transcripts mentions the bakery.

--checking the three mentioned interviews
select * from interviews  where day=28 and month=7 and year=2021 and transcript like '%baker%' limit 10;
--161 | Ruth    | 2021 | 7     | 28  | Sometime within ten minutes of the theft, I saw the thief get into a car in the bakery parking lot and drive away. If you have security footage from the bakery parking lot, you might want to look for cars that left the parking lot in that time frame.                                                          |
--| 162 | Eugene  | 2021 | 7     | 28  | I don't know the thief's name, but it was someone I recognized. Earlier this morning, before I arrived at Emma's bakery, I was walking by the ATM on Leggett Street and saw the thief there withdrawing some money.                                                                                                 |
--| 163 | Raymond | 2021 | 7     | 28  | As the thief was leaving the bakery, they called someone who talked to them for less than a minute. In the call, I heard the thief say that they were planning to take the earliest flight out of Fiftyville tomorrow. The thief then asked the person on the other end of the phone to purchase the flight ticket.

--checking for license plate according to first interview
select * from bakery_security_logs join people on bakery_security_logs.license_plate=people.license_plate where day=28 and month=7 and year=2021;
--possible plate of the theft:
/*260 | 2021 | 7     | 28  | 10   | 16     | exit     | 5P2BI95       | 221103 | Vanessa | (725) 555-4692 | 2963008352      | 5P2BI95       |
| 261 | 2021 | 7     | 28  | 10   | 18     | exit     | 94KL13X       | 686048 | Bruce   | (367) 555-5533 | 5773159633      | 94KL13X       |
| 262 | 2021 | 7     | 28  | 10   | 18     | exit     | 6P58WS2       | 243696 | Barry   | (301) 555-4174 | 7526138472      | 6P58WS2       |
| 263 | 2021 | 7     | 28  | 10   | 19     | exit     | 4328GD8       | 467400 | Luca    | (389) 555-5198 | 8496433585      | 4328GD8       |
| 264 | 2021 | 7     | 28  | 10   | 20     | exit     | G412CB7       | 398010 | Sofia   | (130) 555-0289 | 1695452385      | G412CB7       |
| 265 | 2021 | 7     | 28  | 10   | 21     | exit     | L93JTIZ       | 396669 | Iman    | (829) 555-5269 | 7049073643      | L93JTIZ       |
| 266 | 2021 | 7     | 28  | 10   | 23     | exit     | 322W7JE       | 514354 | Diana   | (770) 555-1861 | 3592750733      | 322W7JE       |
| 267 | 2021 | 7     | 28  | 10   | 23     | exit     | 0NTHK55       | 560886 | Kelsey  | (499) 555-9472 | 8294398571      | 0NTHK55       |
| 268 | 2021 | 7     | 28  | 10   | 35     | exit     | 1106N58       | 449774 | Taylor  | (286) 555-6063 | 1988161715      */

--checking for transaction in legget street on that day according to interview number two
select * from atm_transactions join bank_accounts on atm_transactions.account_number=bank_accounts.account_number where day=28 and month=7 and year=2021 and atm_location='Leggett Street';
/*id  | account_number | year | month | day |  atm_location  | transaction_type | amount | account_number | person_id | creation_year |
+-----+----------------+------+-------+-----+----------------+------------------+--------+----------------+-----------+---------------+
| 246 | 28500762       | 2021 | 7     | 28  | Leggett Street | withdraw         | 48     | 28500762       | 467400    | 2014          |
| 264 | 28296815       | 2021 | 7     | 28  | Leggett Street | withdraw         | 20     | 28296815       | 395717    | 2014          |
| 266 | 76054385       | 2021 | 7     | 28  | Leggett Street | withdraw         | 60     | 76054385       | 449774    | 2015          |
| 267 | 49610011       | 2021 | 7     | 28  | Leggett Street | withdraw         | 50     | 49610011       | 686048    | 2010          |
| 269 | 16153065       | 2021 | 7     | 28  | Leggett Street | withdraw         | 80     | 16153065       | 458378    | 2012          |
| 275 | 86363979       | 2021 | 7     | 28  | Leggett Street | deposit          | 10     | 86363979       | 948985    | 2010          |
| 288 | 25506511       | 2021 | 7     | 28  | Leggett Street | withdraw         | 20     | 25506511       | 396669    | 2014          |
| 313 | 81061156       | 2021 | 7     | 28  | Leggett Street | withdraw         | 30     | 81061156       | 438727    | 2018          |
| 336 | 26013199       | 2021 | 7     | 28  | Leggett Street | withdraw         | 35     | 26013199       | 514354    | 2012*/

--I found a match for person with id=467400 & id=396669 & id=686048 & id=449774

--checking phone calls according to third interview
select * from phone_calls join people on phone_calls.caller=people.phone_number where day=28 and month=7 and year=2021 and duration<90;
--down to two person: id=686048 & id=449774 (higher chances for id=449774 since call duration was less then 60seconds)

--checking flight on the day after out of fifhtyville in the morning
select * from flights join airports on flights.origin_airport_id=airports.id where airports.city='Fiftyville' and day=29 and month=7 and year=2021 order by hour;
--getting flight_id=36 to New York City. checking if the candidate thief are on that flight
select * from passengers join people on passengers.passport_number=people.passport_number where flight_id=36 and people.id in (686048,449774);
/*+-----------+-----------------+------+--------+--------+----------------+-----------------+---------------+
| flight_id | passport_number | seat |   id   |  name  |  phone_number  | passport_number | license_plate |
+-----------+-----------------+------+--------+--------+----------------+-----------------+---------------+
| 36        | 1988161715      | 6D   | 449774 | Taylor | (286) 555-6063 | 1988161715      | 1106N58       |
| 36        | 5773159633      | 4A   | 686048 | Bruce  | (367) 555-5533 | 5773159633      | 94KL13X       |*/

(676) 555-6554
(375) 555-8161