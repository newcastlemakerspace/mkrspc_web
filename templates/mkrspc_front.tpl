
<!DOCTYPE html>
<head>
  <meta charset="utf-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>{{title}}</title>
  <link rel="stylesheet" type="text/css" href="/static/ncms.css">
  <link rel="stylesheet" href="/static/font-awesome-4.1.0/css/font-awesome.min.css">
</head>

<body id="home">

    <div id='page'>

        <div id='header'>
            <div id='site-name'>Newcastle Makerspace</div>
            <div id='navigation'>
                <span id='user-greeting'> {{user_message}} </span>
                {{!menu}}
            </div>

        </div> <!-- header -->


        <div id='page-content'>

            {{!main_content}}

        </div>
    </div> <!-- page -->
</body>



</html>
