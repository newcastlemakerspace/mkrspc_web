% page_type = "wiki"
% rebase('templates/mkrspc_wiki_base.tpl')

%if allow_edit == True:
    <div class="wiki_edit_toolbar">
        <a href="/wiki/edit/{{slug}}"><i class="fa fa-pencil-square-o fa-fw"></i>Edit page</a>
    </div>
%end

<h2 class="page-title">{{article_title}}</h2>
<div id="wiki_article">
{{!main_content}}
</div>

