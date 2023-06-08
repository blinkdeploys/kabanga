# Kabanga Data Model Architecture (Django + Postgres + Redis on Docker)

## Table of Contents


***************************************************

Paths
* Shopper
    * Request for a Return
    * Purchase an Item
        * Search for the Product
            * Enter search keywords
            * Search by Categories
            * Browse the Catalog
    * Find the Product
        * Click on Product Tile
    * Add to the Cart
        * Click on "Add to Cart" button or icon
    * Complete Order
        * Enter Payment details
        * Click on "Complete Order" Button
    * Track Delivery
        * Pending
        * Gathering Order
        * Packaging
        * Shipping (Tracking Code Available)
        * Product in City
        * Delivered
* StoreOwner
    * List Product Items
    * Accept Orders
    * Handling Shipping
    * Handling Returns
* Courier
* Administor
    * Run management scripts

***************************************************

## A. Context

## DATA MODELS


### ACCOUNT:

### User                |
    Fields              | pk, name, email, password, contact_number, address, zip_code,
                        | user_group_id
    Relationships       |
                        | None
    Notes               | User account
### User Group          |
    Fields              | pk, title
    Values              | Guest, Shopper, StoreOwner, Courier, Administrator
    Notes               |
                        | User account groups
### MailingAddress      |
    Fields              | pk, user_id, street, city, state, country, zip_code
    Relationships       |
                        | user_id           (foreign key to User table)
    Notes               |
                        | List of user's mailing addresses
### WalletType          |
    Fields              | pk, title
    Values              | Credit, Debit, EBT, Gift Card, PayPal
    Notes               |
                        | Category of Payment Method (credit, debit, gift card, EBT etc)
### Wallet              |
    Fields              | pk, user_id, wallet_type_id, card_number, full_name, billing address, zip_code
    Relationships       |
                        | user_id           (foreign key to User table)
                        | wallet_type_id    (foreign key to WalletType table)
    Notes               | Payment Methods   (list of user card information, md5 encrypted)

### PRODUCT:

### ProductCategory     |
    Fields              | pk, title, description, geo (locations found in)
    Relationships       | 
                        | None
    Notes               | Product Category listing
### Product             |
    Fields              | pk, product_category_id, code, title, description, price, image_url,
                        | availability
    Relationships       | 
                        | product_category_id (foreign key referencing ProductCategory Table)
    Notes               | Product listing and description
### Review              |
    Fields              | pk, user_id, product_id, rating, comment
    Relationships       |
                        | user_id               (foreign key referencing User Table)
                        | product_id            (foreign key referencing Product Table)
    Notes               | Product reviews

### STORE:

### Store               |
    Fields              | pk, title, address, contact_number, operating_hours,
    Relationships       | 
                        | None
    Notes               | Store offering products on the service
### Store Rep           |
    Fields              | pk, store_id, first_name, last_name, address, contact_number,
                        | operating_hours,
    Relationships:      | 
                        | store_id (foreign key referencing Store Table)
    Notes               | Contact person / owner of store
### ProductItem         |
    Fields              | pk, store_id, code, title, description, price, image_url
                        | availability
    Relationships       |
                        | store_id              (foreign key referencing Store Table)
                        | product_id            (foreign key referencing Product Table)
    Notes               | This is a Product Item that is sold by a store
### ProductItemImage    |
    Fields              | pk, url, product_item_id
    Relationships       |
                        | product_item_id       (foreign key referencing ProductItem Table)
    Notes               | List of product images for product items sold in a store
### Inventory           |
    Fields              | pk, product_id, quantity, reorder_point, last_recount_date
    Relationships       |
                        | product_item_id       (foreign key referencing ProductItem Table)
    Notes               | This is a Product Item that is sold by a store.
                        | The reorder_point the quantity at which the store owner is
                        | notified to replinish stock

### ORDER:

### Order               |
    Fields              | pk, user_id, store_id, status, payment_details
    Relationships       |
                        | user_id   (foreign key referencing User Table)
                        | store_id  (foreign key referencing Store Table)
### OrderItem           |
    Fields              | pk, order_id, product_id, quantity, price, discount_id
    Relationships       |
                        | order_id      (foreign key referencing Order Table)
                        | product_id    (foreign key referencing Product Table)
                        | discount_id   (foreign key referencing Discount Table)
    Notes               | A single product item in a customer's cart
### TransactionStatus   |
    Fields              | pk, code, title
    Values              | Pending, Refund, Failed, Successful
    Relationships       |
                        | None
    Notes               | Payment transaction status
### PaymentTransaction  |
    Fields              | pk, user_id, order_id, transaction_status_id, 
                        | amount, payment_method, gateway_meta, timestamp
    Relationships       |
                        | user_id               (foreign key referencing User Table)
                        | order_id              (foreign key referencing Order Table)
                        | transaction_status_id (foreign key referencing TransactionStatus Table)
    Notes               | Records of payment transactions
                        | gateway_meta: Meta data sent from the associated gateway during transaction
### DiscountType        |
    Fields              | pk, code, title
    Values              | Customer, ProductItem, Store, Promotion
    Relationships       |
                        | user_id               (foreign key referencing User Table)
    Notes               | List of discount types
                        | Customer: discount applied to a single customer
                        | ProductItem: discount applied toa single ProductItem
                        | Store: discount applied to all items sold by a store customer
                        | Promotion: discount applied to all items in the service
### Discount            |
    Fields              | pk, code, title, discount_amount, description,
                        | discount_type_id, discount_owner_id
                        | start_datetime, expiration_datetime
    Relationships       |
                        | discount_type_id      (foreign key to content type for DiscountType table)
                        | discount_owner_id     (foreign key to record in indicated CT table)
    Notes               |
                        | Discount offered to single customer, for single product, or an entire store
### StoreCredit         |
    Fields              | pk, user_id, order_id, amount, start_datetime, expiration_datetime
    Relationships       |
                        | user_id               (foreign key to content type for User table)
                        | order_id              (foreign key to content type for Order table)
    Notes               |
                        | user_id               (the user that owns the store credit)
                        | order_id              (order that initiated the store credit)
### DELIVERY:

### DeliveryPartner
    Fields              | pk, company_name, contact_number, head_office_address
    Relationships       |
                        | None
    Notes               | Company contracted to devliver items
### DeliveryServiceArea
    Fields              | pk, code, title, landmark
    Relationships       |
                        | None
    Notes               | A location that a user can have good delivered to
### DeliveryZipCode
    Fields              | pk, zip_code, delivery_service_area_id
    Relationships       |
                        | delivery_service_area_id  (foreign key referencing DeliveryServiceArea Table)
    Notes               | List of zip codes in a delivery service area
### DeliverySchedule   
    Fields              | pk, delivery_partner_id, day_of_week, start_time, stop_time
    Relationships       |
                        | delivery_partner_id
    Notes               | Delivery times for each partner
### DeliveryStatus      |
    Fields              | pk, code, title
    Values              | Pending, En-route, Return, Failed, Successful
    Relationships       |
                        | None
    Notes               | Delivery Status
### Delivery            |
    Fields              | pk, order_id, partner_id, delivery_status_id, tracking_id,
                        | estimated_arrival_time
    Relationships       |
                        | order_id              (foreign key referencing Order Table)
                        | partner_id            (foreign key referencing DeliveryPartner Table)
                        | delivery_status_id    (foreign key referencing DeliveryStatus Table)
    Notes               | Record of order delivery after a payment is approved till a product
                        | is delivered or returned

### MISCELLANEOUS:

***************************************************

Lists:
GeoData:
    Cities:
    States:
    Countries:
Product Depatment / Category / Type
Food
    Vegetables
    Meats
    Fish/Seafood
    Ethnic Delicacies
    Flours
    Tubers
    Condiments
        Spices
        Sauces
        Soup Thickeners
    Snacks
    Beans
    Nuts
    Convenience Foods &amp; Cereal
    Oils
    Coffee
    Tea
    Wine
Monthly Deals
Gardening
    Seeds
Body Care
    Beauty
    Health
Services
    Gifts
    Gift Cards
Other
    Accessories


Collections:
Full List:
Banga / Palm
    Fruit
    Seeds
    Oil
Dried Fish
Sweetners / Cubes
Meats
    Goat
    Pork
    Chicken
    Lamb
        GMO
        Free range
        Organic
    Snail
Seafood
    Crayfish
        Whole
        Ground
    Stockfish
        Head
        Whole
        Ground
    Prawns
    Smoked Fish
Garri / Fufu
Semolina
Peppers
Vegetables
    Okra
        Dried
        Fresh
        Dried, Ground
    Ugu
    Water Leaf
    Bitter Leaf
    Oha
    Uchakiri
    Fluted Pumpkin
    Spinach
    Scent leaf
    Banga Leaves
Nuts
    Peanuts
        Whole
        Shelled
        Cooked
        Uncooked
    Bambara (Okpa)
        Ground
        Whole
    Tiger Nuts (Aki Hausa)
Grains
    Rice
        Local
        Basmati
    Couscous
    Dawadawa
    Millet
    Corn
    Sorghum
    Wheat
    Teff
Soup Thickeners
    Ogbono
        Whole
        Ground
    Egusi
        Whole
        Ground
    Achi Soup Thickener
Tomatoes
    Whole
    Canned / Puree
Spices
    Bay Leaf
    Ugba (African Bean Seed Oil)
    Onions (dried)
    Thyme
    Curry (powder)
    Shallots
    Garlic
    Nchuawu
Tubers / Roots
    Potatoes
        Whole
        Ground
    Yams
        Whole
        Ground
    Cassava
    Cocoyam
Beans
    Cowpeas
    Pidgen Peas
    Djasan
Achicha
Cocoyam
Salt
Vegetable Oil
    Banga
    Olive
    Canola
Ceremonial
    Bitter Kola
    Red Kola
Spices
    Spice Mixes
        Pepper Soup
        Suya
Fruit
    Plantain
Drinks / Cocktails
    Palm Wine
    Zobo (Zoborodo)
    Boza
    Mazagran
    Grogue
    Amase
    Oshikundu
    Sobia
    Dawa (Kenya)
Snacks
    Confectionaries
        Meat Pies
            Jamiacan Pies
            Nigerian Pies
            Sausage Pie
            Senegalese Fataya
            Hawawshi
        Kulikuli
        Droewors
        Somali Doughnuts (Kac Kac)
    Street
        Abacha
        Akara (Bean Cake)
        Atieke
        Bole
        Brik
        Ewa Agoyin and Agege Bread
        Kebda Eskandarani (Alexandrian Liver)
        Kushari
        Moi Moi
        Mahjouba
        Nyama Choma
        Potato Bhajia
        Roasted or Boiled Corn
        Vetkoek
        Wanke Rice and Fish
    Okpa (Bambara)
    Akara
    Kebab
    Jerky
    Paste
        Peanut
    Fries
        Akara Fried Bean Buns
        Puff Puff / Kpof Kpof / Koose
        Plantain
        Fried eggs
        Doughnuts
        Koeksister
        Fried yam
        Fried chicken
        Chips
        Chin-chin
        Fried meat
    Suya
Imports
    Coffee
        Ethiopian
        Sudanese
    Wines
        South African Wines
    Palm Wine
Sauces
    Shitto (Black Pepper Sauce)


Groups
    Oils

Processing Markers
    Raw
    Fried
    Dried
    Sun-dried
    Ground
    Cooked
    Shelled
    Peeled
    Pickled 
    Jerky
    Grilled
    Candied

***************************************************

## Ideas:
* Enter Zip Code, see whats in your store
* Discounts, Deals and Promotions: Get X% Off for your next X orders
* Chat with our team
* Privacy Policy
* Return Policy
* Track your Order
* Footer
    * Contact Details
    * Follow / Socials
    * Payments Accepted
    * Sitemap
    * Policy (Privacy and Security)

***************************************************

## F. Setup and Configurations

***************************************************

## G. Resources

Recipes and Food Classifications:
https://afrifoodnetwork.com/
https://www.myplate.gov/eat-healthy/food-group-gallery
https://www.myplate.gov/app/shopsimple?utm_source=shop-simple&utm_medium=redirect&utm_campaign=desktop-redirect
https://afrifoodnetwork.com/articles/african-street-foods/
https://www.thespruceeats.com/african-food-4162459
https://www.tasteatlas.com/most-popular-herbs-and-spices-in-africa
https://boam.com/
https://boam.ai/use-cases

* Docker Compose with Django and Postgresql (deploy multi container with compose yml) https://kimlyvith.medium.com/docker-compose-with-django-and-postgresql-577739697b3f
* Django Rest Framweork https://www.digitalocean.com/community/tutorials/how-to-build-a-modern-web-application-to-manage-customer-information-with-django-and-react-on-ubuntu-18-04
* Frontend https://www.pluralsight.com/guides/how-to-use-react-to-set-the-value-of-an-input
