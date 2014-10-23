<!DOCTYPE html>
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>{{title}}</title>
    <link rel="stylesheet" type="text/css" href="/static/ncms.css">
    <link rel="stylesheet" href="/static/font-awesome-4.1.0/css/font-awesome.min.css">
    <link rel="stylesheet" href="http://code.cdn.mozilla.net/fonts/fira.css">
</head>

<body id="home">
    <div id="page">
        <div id="header">
            <h1 id="site-name" class="right">Newcastle Makerspace</h1>

            %if site_message is not None:
                <div class="site-message"><i class="fa fa-exclamation-triangle"></i> {{!site_message}}</div>
            %end
            %if user_message is not None:
                <div id="user-greeting">{{!user_message}}</div>
            %end
            <div id="navigation">
                {{!menu}}
            </div>

        </div> <!-- header -->

        <div id="page-content">
        {{!base}}
        </div> <!-- page content -->
    </div> <!-- page -->
</body>
</html>
