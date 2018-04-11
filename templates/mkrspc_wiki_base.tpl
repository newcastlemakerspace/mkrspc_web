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
        <div id="user-greeting"> {{!user_message}} </div>
    %end

    <div id="side-nav">
        <div id="header">
            <h1 id="site-name" class="left">Newcastle <br/>Makerspace</h1>

            <div id="navigation">
                {{!menu}}
            </div>

        </div> <!-- header -->
        <div id="wiki-index">
            <h4 class="wiki_index">Wiki index</h4>
            <ul class="wiki_index">
                %for cat in wiki_index:
                    <li class="wiki_index"><a href="/wiki/category/{{cat[0]}}">{{cat[1]}} ({{len(cat[2])}})</a></li>
                    <ul class="wiki_index">
                    %for article in cat[2]:
                        <li class="wiki_index"><a href="/wiki/{{article[0]}}">{{article[1]}}</a></li>
                    %end
                    %for subcat in cat[3]:
                        <li class="wiki_index"><a href="/wiki/category/{{subcat[0]}}">{{subcat[1]}}</a> ({{subcat[2]}})</li>
                    %end
                    </ul>
                %end
            </ul>
        </div> <!-- wiki-index -->

    </div> <!-- side-nav -->
    <div id="page-content">

        %if site_message is not None:
        <div class="site-message"><i class="fa fa-exclamation-triangle"></i> {{!site_message}}</div>
        %end

        {{!base}}

    % include('templates/mkrspc_login_block.tpl')

    </div> <!-- page content -->

</body>
</html>
