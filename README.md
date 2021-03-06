## Реализация API реферальной системы:

Программа запускается стандартной для Django командой:
```
python manage.py runserver
```

Предполагается что на сервере уже установлен Postgresql, с юзером `user`, паролем `password`,
а также существует база данных `db_name`. Все эти переменные вынесены в файл config.py, вам будет 
достаточно вписать там свои данные

У нашей программы будет два эндпоинта:
1. **api/login**

Здесь реализована логика авторизации. Принимает только POST запросы.
Первым запросом отправляем JSON фаил с номером телефона:
```
{    "user":{	"phone": example_user}}
```
Далее спустя 3 секунды (преполагаем что наш сервер выслал код для подтверждения)
отправляем следующий JSON с номером телефона и кодом подтверждения (пишите любое набор из 4х цифр):
```
{    "user":{
		"phone": example_user,
        	"code": "111" }}
```
Здесь же если хотим указать инвайт-код, делаем это:
```
{    "user":{
		"phone": example_user,
        	"code": "111",
		"referal": referal}}
```
В случае если для **example_user** ранее делался запрос на код подтверждения происходит авторизация,
а если пользователь пришел в первый раз, то регистрируем его. Ответом будет JSON фаил,
содержащий следующие данные:
```
{   "user": {
        "phone": example_user,
        "referal": referal,
        "token": token}}
```
Здесь важная часть это токен. Он используется для авторизации юзера, и во всех дальнейших действиях,
связанных с пользовательскими данными он будет необходим, так что сохраняем его. Срок действия токена - 1 сутки, либо 
ближайшее обновление данных.

2. **api/user**

Этот эндпоинт предназначен для работы с авторизованным юзером, поэтому в заголовке **Authorization** запроса необходимо 
указать токен в формате: `"Token" example_token`
Принимает GET и PUT запросы:
* запрос GET выдаст нам информацию по юзеру в следующем виде:
```
{   "user": {
        "phone": example_phone,
        "user_referals": список юзеров, указавших referal в своём профиле,
        "referal": referal}}
```
* запрос PUT позволяет обновить номер телефона (если указанный номер ещё не регистрировался),
и указать инвайт-код(если он не был указан при регистрации). Данные указываем в формате:
```
{	"user": {
        "phone": new_phone,}}
```
