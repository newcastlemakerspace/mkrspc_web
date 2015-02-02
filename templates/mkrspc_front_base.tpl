<!DOCTYPE html>
<head xmlns="http://www.w3.org/1999/html">
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>{{title}}</title>
    <link rel="stylesheet" type="text/css" href="/static/ncms.css">
    <link rel="stylesheet" href="/static/font-awesome/css/font-awesome.min.css">
    <link rel="stylesheet" href="http://code.cdn.mozilla.net/fonts/fira.css">
</head>

<body id="home" class="{{page_type}}">

    %if user_message is not None:
        <div id="user-greeting">{{!user_message}}</div>
    %end

    <div id="page">
        <div id="header">
            <h1 id="site-name" class="right">Newcastle Makerspace</h1>

            <div id="navigation">
                {{!menu}}
            </div>

        </div> <!-- header -->

        <div id="page-content">

            %if site_message is not None:
                <div class="site-message"><i class="fa fa-exclamation-triangle"></i> {{!site_message}}</div>
            %end

            {{!base}}

        </div> <!-- page content -->
    </div> <!-- page -->
</body>
</html>
