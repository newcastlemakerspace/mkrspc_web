

<!DOCTYPE html>
<head xmlns="http://www.w3.org/1999/html">
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>{{title}}</title>
    <link rel="stylesheet" type="text/css" href="/static/ncms.css">
    <link rel="stylesheet" href="/static/font-awesome-4.1.0/css/font-awesome.min.css">
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

<%
from models.site_message import SiteMessage
%>

            %if site_message is not None:
                %if isinstance(site_message, basestring):
                    <div class="broken_site_message"><i class="fa fa-exclamation-circle"></i> ::FIX THIS SITE MESSAGE:: <img src="FIXME_404_for_logs.png"/> {{!site_message}}</div>
                %end
                %if isinstance(site_message, SiteMessage):
                    <div class="{{site_message.css_class}}"><i class="fa {{site_message.icon}}"></i> {{!site_message.message}}</div>
                %end
            %end

            {{!base}}

        </div> <!-- page content -->
    </div> <!-- page -->
</body>
</html>
