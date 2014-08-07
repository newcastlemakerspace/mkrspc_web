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
            <h1 id='site-name'>Newcastle Makerspace</h1>
            <div id='navigation'>
                {{!menu}}
            </div>
        </div> <!-- header -->
        <div id='page-content'>
            <p> wiki page </p>

            %if editable == True:

                <div id="form_container">

                    <form id="wiki_controls" class="wikiform"  method="post" action="/wiki_update">

                        <textarea rows="60" cols="81" class="ncms_textarea">Mark down hard-coded here
=========
as a test

Is this indented right?

    This should be code?

                        </textarea>
                        <input type="hidden" name="form_id" value="33456" />
                        <input id="save_wiki" class="ncms_buttons" type="submit" name="submit" value="Save" />
                        <input id="preview_wiki" class="ncms_buttons" type="submit" name="submit" value="Preview" />
                        <input id="preview_wiki" class="ncms_buttons" type="submit" name="submit" value="Preview" />
                    </form>
                </div>

                <h1>Edit button!!</h1>

            %end

            {{!main_content}}
        </div>



    </div> <!-- page -->
</body>



</html>
