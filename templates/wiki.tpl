% include('templates/mkrspc_wiki_header.tpl')

%if allow_edit == True:
  <div class="wiki_edit_toolbar">
      <a href="/wiki/edit/{{slug}}"><i class="fa fa-pencil-square-o fa-fw"></i>Edit page</a>
      <i class="fa fa-times fa-fw"></i>Cancel
      <i class="fa fa-check-square-o fa-fw"></i>Save
  </div>
%end


{{!main_content}}


% include('templates/mkrspc_wiki_footer.tpl')
