from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def index_view(request):
    context = {
        'highlights': [
            {
                'price': '$69.99',
                'title': 'GCI Outdoor Freestyle Rocker',
                'image': 'https://img.freepik.com/free-vector/beautiful-frame-with-edges-cooking-herbs-placers-spices-wooden-dishes_1284-6093.jpg?size=338&ext=jpg',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$45.99',
                'was': '$84.99',
                'image': 'https://diabetestalk.net/images/wxOaHogUtrtqUTGE.jpg',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'detail': 'It\'s not Latin, though it looks like it, and it actually says nothing',
            },
        ],
        'spice_highlights': [
            {
                'price': '$69.99',
                'image': 'https://tarateaspoon.com/wp-content/uploads/2018/02/SI_12_Ways_Beauty_feature-300x300.jpg',
                'title': 'Appetizers and Nibbles',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$8.99',
                'was': '$28.99',
                'image': 'https://image.freepik.com/free-photo/tasty-baked-chicken-legs-with-spices-pan_1220-3194.jpg',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'detail': 'It\'s not Latin, though it looks like it, and it actually says nothing',
            },
            {
                'price': '$8.99',
                'image': 'https://i.pinimg.com/736x/f3/b3/a3/f3b3a3e7509d62d16e56ced41651dbed.jpg',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'detail': 'Sprouts Organic Paprika Powder Spice',
            },
            {
                'price': '$28.99',
                'image': 'http://img.21food.com/20110609/product/1307149718348.jpg',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$28.99',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'image': 'https://i.pinimg.com/236x/33/cf/74/33cf743ef0784f7ceb4f78ed2778cdb7.jpg?nii=t',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$28.99',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'image': 'https://www.herbies.com.au/wp-content/uploads/images/products/p-538-_DSC0745.jpg',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$28.99',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'image': 'https://i.pinimg.com/236x/68/26/bb/6826bb389a93cedcc62284a412974418.jpg?nii=t',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$28.99',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'image': 'https://www.southafricantaste.ch/wp-content/uploads/2020/10/ina-paarman-08-300x300.jpeg',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$28.99',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'image': 'https://www.smells-like-home.com/wp-content/uploads/2019/06/BBQ-Spice-Rub-Recipe-large-1-480x480.jpg',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$28.99',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'image': 'https://cdn.shopify.com/s/files/1/0221/1304/files/iStock_000047605750_Small_large.jpg?6209702599144734334',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$28.99',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'image': 'https://res.cloudinary.com/yuppiechef/image/upload/c_lpad,e_sharpen:40,h_233,q_auto,w_233/v1/category/1311/matrix34colPicture1448884332',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
            {
                'price': '$28.99',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'image': 'https://husainfoodstuff.com/images/spices-9.jpg',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
        ],
        'deal_highlights': [
            {
                'price': '$55.99',
                'was': '$30.50',
                'image': 'https://i.pinimg.com/736x/78/a0/9e/78a09e6ff7c3a471e7b4d2bca18bff24.jpg',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'detail': 'It\'s not Latin, though it looks like it, and it actually says nothing',
            },
            {
                'price': '$45.99',
                'was': '$36.99',
                'image' :'https://i.pinimg.com/236x/e4/08/29/e4082911d9bcd23b07fdecc047cb53fa.jpg?nii=t',
                'title': 'Appetizers and Nibbles',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
        ],

        'meals': [
            {
                'starting': '$29.50',
                'price': '$76.00',
                'was': '$76.00',
                'image': 'https://freepngimg.com/thumb/food/139184-food-plate-healthy-free-photo-thumb.png',
                'title': 'Burberry Touch Eau De Toilette',
                'detail': 'Cologne For Men, 1.7 Oz',
                'rating': 4,
            },
            {
                'starting': '$127.00',
                'price': '$127.00',
                'image': 'https://shk-images.s3.amazonaws.com/wp-content/uploads/2014/09/large_Choose-MyPlate-breakfast-Egg-and-Peaches.jpg',
                'title': 'Expert Grill 28"',
                'detail': 'Offset Charcoal Smoker Grill with Side Firebox, Black',
            },
            {
                'starting': '$22.18',
                'price': '$22.18',
                'was': '$244.99',
                'image': 'https://specialdocs.com/wp-content/uploads/2017/11/AICR_NewAmericanPlate-824x824-1.png',
                'title': 'Zebco 202 Spincast Fishing Combo With Tackle Kit',
                'detail': 'Deserunt mollit anim id est laborum.',
            },
            {
                'price': '$64.50',
                'image': 'https://www.restaurants-guide4u.com/recipes/reference/92/Amazing_Lam_Rack.jpg',
                'title': 'The Legend of Zelda: Tears of the Kingdom',
                'detail': 'Tears of the Kingdom for the Nintendo Switch',
            },
            {
                'price': '$148.95',
                'was': '$164.99',
                'image': 'https://s.pngkit.com/png/small/15-151290_find-restaurant-restaurant-food-plate-image-png.png',
                'title': 'Beats Studio Buds',
                'detail': 'True Wireless Noise Cancelling Bluetooth Earbuds - Black',
            },
            {
                'price': '$3.99',
                'was': '$9.99',
                'image': 'https://purepng.com/public/uploads/thumbnail/purepng.com-food-plate-top-viewfood-objects-plate-941524640234npd6c.png',
                'title': 'Sprouts Organic Garlic Powder',
                'detail': 'Sunt in culpa qui officia',
                'rating': 3,
            },
            {
                'price': '$2.50',
                'image': 'https://img.favpng.com/16/10/12/health-food-healthy-diet-meal-delivery-service-png-favpng-a1gPUmX28YxaV48SnQtD3zgLj.jpg',
                'title': 'Great Value Garlic Powder',
                'detail': 'Lorem ipsum dolor sit amet',
                'rating': 3.4,
            },
            {
                'price': '$5.99',
                'image': 'https://freepngimg.com/thumb/food/139184-food-plate-healthy-free-photo-thumb.png',
                'title': 'Great Value Lemon & Pepper Seasoning',
                'detail': 'Consectetur adipiscing elit,',
                'rating': 2,
            },
        ],

        'spices': [
            {
                'price': '$4.50',
                'image': 'https://sysuinc.com.ph/storage/products/77/McCormick%20Rosemary%20Leaves%20Whole%2011g.jpg',
                'title': 'Sprouts Organic All-Purpose Seasoning',
                'detail': 'Sed do eiusmod tempor incididunt',
            },
            {
                'price': '$3.99',
                'was': '$5.99',
                'image': 'https://i5.walmartimages.com/asr/37499e13-8c86-425f-b584-a70d2af5826d_1.bfd36d7eace35ce1a5487f5a320d3b89.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF',
                'title': 'McCormick® Roasted Garlic & Herb Seasoning',
                'detail': 'Ut labore et dolore magna aliqua.',
            },
            {
                'price': '$2.99',
                'was': '$5.99',
                'image': 'https://i5.walmartimages.com/asr/07e1ef85-90d0-48df-a85d-0ced65237360_1.916abe61f3f87c1da2d6607dd2c5bcb9.jpeg?odnHeight=450&odnWidth=450&odnBg=ffffff',
                'title': 'Supreme Tradition Cilantro Leaves',
                'detail': 'Ut enim ad minim veniam',
                'rating': 4.5,
            },
            {
                'price': '$6.99',
                'image': 'https://mouthsofmums.com.au/wp-content/uploads/2016/05/355473.jpg',
                'title': 'Sprouts Organic Salt-Free Italian Seasoning',
                'detail': 'Quis nostrud exercitation ullamco',
            },
            {
                'price': '$5.45',
                'image': 'http://scene7.samsclub.com/is/image/samsclub/0005210030218_A?$img_size_380x380$',
                'title': 'Sprouts Organic Salt-Free Lemon Pepper Seasoning',
                'detail': 'Laboris nisi ut aliquip',
                'rating': 3,
            },
            {
                'price': '$1.45',
                'image': 'https://www.zallat.com/wp-content/uploads/2019/01/Simply-Organic-Bottled-Spice-Curry-Powder-18763-front_12-1-350x350.jpg',
                'title': 'Supreme Tradition Chopped Chives',
                'detail': 'Ex ea commodo consequat.',
                'rating': 4,
            },
            {
                'price': '$1.05',
                'image': 'https://www.keepcalmandcoupon.com/wp-content/uploads/2019/07/simply-organic-bottled-spices.jpeg',
                'title': 'Supreme Tradition Garlic & Pepper Seasoning',
                'detail': 'Excepteur sint occaecat',
            },
            {
                'price': '$2.40',
                'was': '$4.50',
                'image': 'https://zallat.com/wp-content/uploads/2019/01/f3d7301e53f4d0d81b4d60c4b8ba738a_416x416.jpg',
                'title': 'Old Spice High Endurance Anti-Perspirant Deodorant, 48 Hour Protection, Pure Sport Scent',
                'detail': 'Cupidatat non proident,',
            },
            {
                'price': '$9.99',
                'was': '$14.50',
                'image': 'https://m.media-amazon.com/images/I/41uMDfqZLNL.jpg',
                'title': 'Supreme Tradition Italian Seasoning',
                'detail': 'Sunt in culpa qui officia',
            },
            {
                'price': '$3.78',
                'image': 'https://images.albertsons-media.com/is/image/ABS/960530894?$ecom-pdp-desktop$&defaultImage=Not_Available&defaultImage=Not_Available',
                'title': 'Supreme Tradition Garlic Pepper Seasoning',
                'detail': 'Deserunt mollit anim id est laborum.',
            },
            {
                'price': '$28.99',
                'title': 'Sprouts Organic Paprika Powder Spice',
                'image': 'https://i2.wp.com/wholefully.com/wp-content/uploads/2012/12/spice-rub-hero-480x480.jpg',
                'detail': 'Until recently, the prevailing view assumed lorem ipsum was born as a nonsense text.',
            },
        ],

        'spice_deals': [
            {
                'price': '$12.55',
                'was': '$35.50',
                'image': 'https://res.cloudinary.com/yuppiechef/image/upload/c_lpad,e_sharpen:40,h_233,q_auto,w_233/v1/contentdocs/36587/otherpicture520180213102726',
                'title': 'Spice Time Pure Ground Black Pepper',
                'detail': 'Quis nostrud exercitation ullamco',
                'rating': 5,
            },
            {
                'price': '$18.50',
                'was': '$28.50',
                'image': 'https://m.media-amazon.com/images/I/418DSjherfL.jpg',
                'title': 'Sprouts Organic Cayenne Pepp Ground Spice',
                'detail': 'Excepteur sint occaecat',
            },
            {
                'price': '$23.50',
                'was': '$34.50',
                'image': 'http://ii.worldmarket.com/fcgi-bin/iipsrv.fcgi?FIF=/images/worldmarket/source/57595_XXX_v1.tif&wid=420&cvt=jpeg',
                'title': 'Tony Chachere\'s Creole Foods Creole Seasoning',
                'detail': 'Sunt in culpa qui officia',
            },
        ],
        # https://images.sks-bottle.com/images/16oz-spice-container_resize.jpg
        # https://ww1.prweb.com/prfiles/2008/09/09/299382/FRChipotleSesameGroupLoRes.jpg

        'sides': [
            {
                'title': 'Departments',
            },
            {
                'title': 'Lorem ipsum dolor sit amet',
            },
            {
                'title': 'Consectetur adipiscing elit,',
            },
            {
                'title': 'Stores',
            },
            {
                'title': 'Sed do eiusmod tempor incididunt',
            },
            {
            'title': 'Ut labore et dolore magna aliqua.',
            },
            {
            'title': 'Tracking',
            },
            {
            'title': 'Ut enim ad minim veniam',
            },
            {
            'title': 'Quis nostrud exercitation ullamco',
            },
            {
            'title': 'My Orders',
            },
            {
            'title': 'Laboris nisi ut aliquip',
            },
            {
            'title': 'Ex ea commodo consequat.',
            },
            {
            'title': 'Track Deliveries',
            },
            {
            'title': 'Excepteur sint occaecat',
            },
            {
            'title': 'Cupidatat non proident,',
            },
            {
            'title': 'Holiday Deals',
            },
            {
            'title': 'Sunt in culpa qui officia',
            },
            {
            'title': 'Deserunt mollit anim id est laborum.',
            }
        ],

        'sections': [
            {
                'title': 'The passage experienced a surge in popularity',
            },
            {
                'title': 'During the 1960s when Letraset used it on their dry-transfer sheets',
            },
            {
                'title': 'And again during the 90s as desktop publishers bundled the text',
            },
            {
                'title': 'With their software. Today it\'s seen all around the web; on templates, websites',
            },
            {
                'title': 'Stock designs. Use our generator to get your own,',
            },
            {
                'title': 'Or read on for the authoritative history of lorem ipsum.',
            },
        ],

        'prices': [
            {
                'title': 'Richard McClintock, a Latin scholar',
            },
            {
                'title': 'Hampden-Sydney College',
            },
            {
                'title': 'Is credited with discovering',
            },
            {
                'title': 'Source behind the ubiquitous filler text.',
            },
            {
                'title': 'In seeing a sample of lorem ipsum',
            },
            {
                'title': 'His interest was piqued by consectetur—a',
            },
            {
                'title': 'Genuine, albeit rare, Latin word.',
            },
            {
                'title': 'Consulting a Latin dictionary',
            },
            {
                'title': 'Led McClintock to a passage',
            },
            {
                'title': 'From De Finibus Bonorum et Malorum',
            },
            {
                'title': 'On the Extremes of Good and Evil),',
            },
            {
                'title': 'A first-century B.C. text',
            },
            {
                'title': 'from the Roman philosopher Cicero.',
            },
            {
                'title': 'In particular, the garbled words',
            },
            {
                'title': 'lorem ipsum bear an unmistakable',
            },
            {
                'title': 'Resemblance to sections 1.10.32-33',
            },
            {
                'title': 'Cicero\'s work, with the',
            },
            {
                'title': 'Most notable passage excerpted below:',
            },
            {
                'title': 'Neque porro quisquam est, qui dolorem',
            },
            {
                'title': 'Dpsum quia dolor sit amet',
            },
            {
                'title': 'Consectetur, adipisci velit, sed quia',
            },
            {
                'title': 'Non numquam eius modi tempora',
            },
            {
                'title': 'Incidunt ut labore et dolore magnam',
            },
            {
                'title': 'Aliquam quaerat voluptatem.',
            },
        ],

        # https://i.pinimg.com/236x/58/21/90/5821905c271d1ea75f399c4c442a7f2e.jpg
        # https://cdn1.vectorstock.com/i/thumb-large/26/10/logo-for-spices-vector-19732610.jpg
        # https://cdn1.vectorstock.com/i/thumb-large/68/30/spice-shop-logo-round-linear-logo-chili-pepper-vector-27596830.jpg
        # https://cdn3.vectorstock.com/i/thumb-large/31/97/herbs-and-spices-logo-watercolor-seamless-pattern-vector-20393197.jpg

        'navigation': [
            [
                {
                    'title': 'Departments',
                    'details': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit,',
                    'url': '/poll/result/stations/',
                    'theme': 'text-dark bg-light',
                    'image': 'https://media.istockphoto.com/vectors/spices-logo-vector-id1151068374?k=6&m=1151068374&s=170667a&w=0&h=9trhCIrIyO8PP5wUOtQgjI7_WY-M_57trarF3doS6RM=',
                },
                {
                    'title': 'Stores',
                    'details': 'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                    'url': '/poll/result_approvals/',
                    'theme': 'text-dark bg-light',
                    'image': 'https://www.shutterstock.com/image-vector/spice-logo-type-vector-template-260nw-1409163959.jpg',
                },
            ],
            [
                {
                    'title': 'Tracking',
                    'details': 'Ut enim ad minim veniam, quis nostrud exercitation ullamco',
                    'url': '/reports/dashboard',
                    'theme': 'text-light bg-dark',
                    'image': 'https://thumb9.shutterstock.com/image-photo/stock-vector-mustard-natural-spices-compilation-of-vector-sketches-kitchen-herbs-and-spice-vintage-style-450w-213435682.jpg',
                },
                {
                    'title': 'My Orders',
                    'details': 'Laboris nisi ut aliquip ex ea commodo consequat.',
                    'url': '/reports',
                    'theme': 'text-dark bg-light',
                    'image': 'https://www.thelogomix.com/files/imagecache/v3-logo-detail/spic.jpg',
                },
                # {
                #     'title': 'Review Agents',
                    # 'details': 'Duis aute irure dolor in reprehenderit in voluptate',
                #     'url': '/people/agents',
                #     'theme': 'text-dark bg-light',
                # },
                # {
                #     'title': 'Review Candidates',
                    # 'details': 'Velit esse cillum dolore eu fugiat nulla pariatur.',
                #     'url': '/people/candidates',
                #     'theme': 'text-dark bg-light',
                # },
            ],
            [
                {
                    'title': 'Track Deliveries',
                    'details': 'Excepteur sint occaecat cupidatat non proident,',
                    'url': '/geo',
                    'theme': 'text-dark bg-light',
                    'image': 'https://image.shutterstock.com/image-vector/herbs-spices-icon-hand-drawn-260nw-1405065824.jpg',
                },
                {
                    'title': 'Holiday Deals',
                    'details': 'Sunt in culpa qui officia deserunt mollit anim id est laborum.',
                    'url': '#',
                    'theme': 'text-dark bg-light',
                    'image': 'https://seeklogo.com/images/M/mom-s-quality-spices-logo-5CEC6AFDD0-seeklogo.com.png',
                },
            ],
        ],
    }
    return render(request, "home.html", context)
