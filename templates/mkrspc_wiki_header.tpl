<!DOCTYPE html>
<head xmlns="http://www.w3.org/1999/html">
  <meta charset="utf-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>{{title}}</title>
  <link rel="stylesheet" type="text/css" href="/static/ncms.css">
  <link rel="stylesheet" href="/static/font-awesome-4.1.0/css/font-awesome.min.css">
  <link rel="stylesheet" href="http://code.cdn.mozilla.net/fonts/fira.css">
    <style>

#side-nav
{
	clear: left;
	float: left;
	width: 18%;
	display: inline;
}

#page-content
{
	float: right;
	width: 75%;
	display: inline;
}

    </style>

</head>
<body id="home">

        <div id="side-nav">
            <div id="header">
                <h1 id="site-name" class="left">Newcastle <br/>Makerspace</h1>
                <div id="navigation">
                    %if user_message is not None:
                    <div id="user-greeting"> {{!user_message}} </div>
                    %end
                    {{!menu}}
                </div>
            </div> <!-- header -->

			<h3>
				Wiki index
			</h3>
			<p>
                <ul class="wiki_index">
                   %for cat in wiki_index:
                     <li class="wiki_index">{{cat[1]}}</li>
                     <ul class="wiki_index">
                     %for subcat in cat[2]:
                        <li class="wiki_index"><a href="/wiki/subcat/{{subcat[0]}}">{{subcat[1]}}</a></li>
                     %end
                     </ul>
                   %end
                </ul>
			</p>
		</div>
        <div id="page-content">
