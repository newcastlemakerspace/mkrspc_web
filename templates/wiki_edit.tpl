% include('templates/mkrspc_wiki_header.tpl')

<div class="wiki_edit_toolbar">
  <i class="fa fa-pencil-square-o fa-fw"></i>Edit page
  <a href="#" onclick="alert('not implemented yet..');"><i class="fa fa-times fa-fw"></i>Cancel</a>
  <a href="#" onclick="alert('not implemented yet..');"><i class="fa fa-check-square-o fa-fw"></i>Save</a>
</div>

{{!main_content}}

%if editable == True:
<div id="form_container">

    <form id="wiki_controls" class="wikiform"  method="post" action="/wiki_update">

        <textarea rows="30" cols="72" class="ncms_textarea">
{{!article_markdown}}
        </textarea>
        <input type="hidden" name="form_id" value="33456" />
        <input id="save_wiki" class="ncms_buttons" type="submit" name="submit" value="Save" />
        <input id="preview_wiki" class="ncms_buttons" type="submit" name="submit" value="Preview" />
        <input id="cancel_wiki" class="ncms_buttons" type="submit" name="submit" value="Cancel" />
    </form>
</div>

%end

% include('templates/mkrspc_wiki_footer.tpl')
