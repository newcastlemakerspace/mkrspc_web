% page_type = "wiki"
% rebase('templates/mkrspc_wiki_base.tpl')

{{!main_content}}

%if editable == True:
<div id="form_container">
    <form id="wiki_controls" class="wiki-form"  method="post" action="/wiki/update_article">
        <input type="hidden" name="article_id" value="{{article_id}}" />
        <ul>
            <li>
                <label class="description" for="article_title">Article title</label>
                <div>
                    <input id="article_title" name="article_title" class="element text medium" type="text" size="72" maxlength="255" value="{{article_title}}"/>
                </div>
            </li>
            <li>
                <label class="description" for="article_markdown">Article body (markdown)</label>
                <div>
                    <textarea id="article_markdown" name="article_markdown" rows="30" cols="100" class="ncms_textarea">{{!article_markdown}}</textarea>
                </div>
            </li>
            <li>
                <div>
                    <input type="hidden" name="form_id" value="33456" />
                    <input id="save_wiki" class="ncms_buttons" type="submit" name="submit" value="Save" />
                    <input id="preview_wiki" class="ncms_buttons" type="submit" name="submit" value="(Preview) wip" disabled/>
                    <input id="cancel_wiki" class="ncms_buttons" type="submit" name="submit" value="(Cancel) wip" disabled/>
                </div>
            </li>
        </ul>
    </form>
</div>

%end

