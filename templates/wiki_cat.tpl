% page_type = "wiki"
% rebase('templates/mkrspc_wiki_base.tpl')

{{!main_content}}

%if editable == True:
<h4 class="page-title">Add wiki article</h4>  <!-- todo need css for all this -->
<div id="wiki_subcat">
    <p>Article will be created in category {{category_name}} [{{category_id}}].</p>
    <form id="wiki_new_article" class="wiki-form"  method="post" action="/wiki/new_article">
        <input type="hidden" name="form_id" value="6846541" />
        <input type="hidden" name="article_cat_id" value="{{category_id}}"/>
        <ul>
            <li>
                <label class="description" for="article_title">Article title</label>
                <div>
                    <input id="article_title" name="article_title" class="element text medium" type="text" maxlength="255" value=""/>
                </div>
            </li>
            <li >
                <label class="description" for="article_slug">Slug (URL string - use only <code>[A-Za-z0-9_-()]</code>)</label>
                <div>
                    <input id="article_slug" name="article_slug" class="element text medium" type="text" maxlength="255" value=""/>
                </div>
            </li>
            <li >
                <div>
                <input id="new_article" class="ncms_buttons" type="submit" name="submit" value="Create" />
                <input id="cancel_wiki" class="ncms_buttons" type="submit" name="submit" value="Cancel" />
                </div>
            </li>
        </ul>

    </form>

</div>

%end




