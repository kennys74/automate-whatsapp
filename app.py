from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://kennys74:kennys74@cluster0.p2qodqv.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    if text is not None:
        number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        msg = res.message("Hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below: "
                          "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* cakes \n 3️⃣ To know our *working hours* \n 4️⃣ "
                          "To get our *address* \n 5️⃣ To *view* our menu")
        msg.media("https://i.ibb.co/BPKnXVP/Red-Velvet-Cake-Waldorf-Astoria.jpg")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message(
                "You can contact us through phone or e-mail.\n\n*Phone*: +277 212 3456 \n*E-mail* : ken@theredvelvet.co.za")
        elif option == 2:
            res.message("You have entered *ordering mode*.")
            users.update_one(
                {"number": number}, {"$set": {"status": "ordering"}})
            res.message(
                "You can select one of the following cakes to order: \n\n1️⃣ Red Velvet (our No 1)  \n2️⃣ Black Forest \n3️⃣ Ice Cream Cake"
                "\n4️⃣ Plum Cake \n5️⃣ Sponge Cake \n6️⃣ Genoise Cake \n7️⃣ Angel Cake \n8️⃣ Carrot Cake \n9️⃣ Fruit Cake  \n0️⃣ Go Back")
        elif option == 3:
            res.message("We work from *8a.m. to 5p.m*.")
        elif option == 4:
            res.message(
                "We have multiple locations across the city. Our main center is at *1 Loop Street, Cape Town*")
        elif option == 5:
            msg = res.message(
                "Please have a look at our delicious cakes available per slice or the whole damm cake!")
            msg.media("https://dynamicwebsolutions.co.za/wp-content/uploads/2022/08/Our-cakes.pdf")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res.message("Please select from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* cakes \n 3️⃣ To know our *working hours* \n 4️⃣ "
                        "To get our *address* \n 5️⃣ To *view* our menu")
        elif 1 <= option <= 9:
            cakes = ["Red Velvet Cake", "Black Forest Cake", "Ice Cream Cake",
                     "Plum Cake", "Sponge Cake", "Genoise Cake", "Angel Cake", "Carrot Cake", "Fruit Cake"]
            selected = cakes[option - 1]
            users.update_one(
                {"number": number}, {"$set": {"status": "address"}})
            users.update_one(
                {"number": number}, {"$set": {"item": selected}})
            res.message("Excellent choice 😉")
            res.message("Please enter your address to confirm the order")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for shopping with us 😊")
        res.message(f"Your order for *{selected}* has been received and will be delivered within an hour")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one(
            {"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting us again.\nPlease select from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* cakes \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.update_one(
            {"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run()
