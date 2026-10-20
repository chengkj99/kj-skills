#!/usr/bin/env python3
"""Validate reading content and render an offline three-mode reader (stdlib only)."""
import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def validate(d):
    errors = []
    def text(value, path):
        if not isinstance(value, str) or not value.strip():
            errors.append(path + ': expected nonempty text')
    def rows(value, path):
        if not isinstance(value, list) or not value:
            errors.append(path + ': expected nonempty list')
            return []
        return value
    if not isinstance(d, dict):
        return ['root must be an object']
    for k in ('title', 'author', 'source', 'source_date', 'overview'):
        text(d.get(k), k)
    paragraphs = rows(d.get('paragraphs'), 'paragraphs')
    ids = {}
    for i, p in enumerate(paragraphs):
        if not isinstance(p, dict):
            errors.append(f'paragraphs[{i}]: expected object'); continue
        expected = f'p{i+1}'
        if p.get('id') != expected:
            errors.append(f'paragraph id must be {expected}')
        ids[expected] = p.get('original', '')
        for k in ('original', 'translation'):
            text(p.get(k), f'{expected}.{k}')
        deep = p.get('deep')
        if not isinstance(deep, dict):
            errors.append(f'{expected}.deep: expected object'); continue
        for k in ('meaning', 'role', 'connection', 'question', 'answer'):
            text(deep.get(k), f'{expected}.deep.{k}')
        if not isinstance(deep.get('details'), list):
            errors.append(f'{expected}.deep.details: expected list')
        else:
            for detail in deep['details']:
                if not isinstance(detail, dict):
                    errors.append('detail must be object'); continue
                for k in ('label', 'text'):
                    text(detail.get(k), 'detail.' + k)
    def ref(item):
        if not isinstance(item.get('paragraph_id'), str) or item.get('paragraph_id') not in ids:
            errors.append('unknown paragraph_id: ' + str(item.get('paragraph_id')))
    for c in rows(d.get('conclusions'), 'conclusions'):
        if not isinstance(c, dict):
            errors.append('conclusion must be object'); continue
        text(c.get('text'), 'conclusion.text')
        for pid in rows(c.get('paragraph_ids'), 'conclusion.paragraph_ids'):
            if not isinstance(pid, str) or pid not in ids:
                errors.append('invalid conclusion reference')
    lang = d.get('language')
    if not isinstance(lang, dict):
        return errors + ['language must be an object']
    text(lang.get('intro'), 'language.intro')
    for item in rows(lang.get('phrases'), 'phrases'):
        if not isinstance(item, dict):
            errors.append('phrase must be object'); continue
        ref(item)
        for k in ('text', 'meaning', 'example', 'example_translation'):
            text(item.get(k), 'phrase.' + k)
    for s in rows(lang.get('sentences'), 'sentences'):
        if not isinstance(s, dict):
            errors.append('sentence must be object'); continue
        ref(s)
        for k in ('original', 'explanation'):
            text(s.get(k), 'sentence.' + k)
        original = s.get('original')
        source = ids.get(s.get('paragraph_id'), '') if isinstance(s.get('paragraph_id'), str) else ''
        if isinstance(original, str) and isinstance(source, str) and original not in source:
            errors.append('training sentence is not verbatim in its paragraph')
        chunks = rows(s.get('chunks'), 'sentence.chunks')
        for ch in chunks:
            if not isinstance(ch, dict):
                errors.append('chunk must be object'); continue
            for k in ('text', 'meaning'):
                text(ch.get(k), 'chunk.' + k)
        if all(isinstance(ch, dict) and isinstance(ch.get('text'), str) for ch in chunks):
            normalize = lambda s: ''.join(s.split())
            if isinstance(original, str) and normalize(''.join(ch['text'] for ch in chunks)) != normalize(original):
                errors.append('chunks must reconstruct original sentence exactly, ignoring whitespace')
    for q in rows(lang.get('exercises'), 'exercises'):
        if not isinstance(q, dict):
            errors.append('exercise must be object'); continue
        ref(q)
        for k in ('prompt', 'answer', 'explanation'):
            text(q.get(k), 'exercise.' + k)
        if q.get('type') not in ('choice', 'cloze', 'open'):
            errors.append('invalid exercise type')
        if q.get('type') == 'choice':
            opts = rows(q.get('options'), 'exercise.options')
            for opt in opts: text(opt, 'option')
            if q.get('answer') not in opts:
                errors.append('choice answer must match an option')
    for item in rows(lang.get('review'), 'review'):
        text(item, 'review item')
    return errors

def e(s):
    return html.escape(str(s), quote=True)

def para(s, cls=''):
    return f'<p class="{cls}">{e(s)}</p>'

def disclosure(label, content):
    return f'<details><summary>{e(label)}</summary>{content}</details>'

def render(d):
    def link(pid, label=None):
        return f'<a href="#quick-{pid}" data-jump="{pid}">{e(label or pid.upper())}</a>'
    def original(p):
        return f'<div class="original" lang="en">{para(p["original"])}</div>'
    def translation(p):
        return f'<div class="translation" lang="zh-CN">{para(p["translation"])}</div>'
    def actions(p):
        return f'<button class="copy" data-copy="{p["id"]}">复制本段追问</button>'
    def header(p):
        return f'<div class="unit-head"><span class="tag">{p["id"].upper()}</span>{actions(p)}</div>'
    def unit(mode, p, inner):
        return f'<article class="unit" id="{mode}-{p["id"]}" data-pid="{p["id"]}">{header(p)}{inner}</article>'
    bilingual = lambda p: '<div class="bilingual">' + original(p) + translation(p) + '</div>'
    conclusions = '<ul>' + ''.join('<li>'+e(c['text'])+' '+' '.join(link(pid) for pid in c['paragraph_ids'])+'</li>' for c in d['conclusions']) + '</ul>'
    quick = '<section class="intro"><h2>先了解这篇文章</h2>'+para(d['overview'])+'<h3>结论、依据与限制</h3>'+conclusions+'</section>'
    quick += ''.join(unit('quick', p, bilingual(p)) for p in d['paragraphs'])
    deep = '<section class="intro"><h2>逐段读懂作者怎样展开</h2><ol>'+''.join('<li>'+link(p['id'])+' '+e(p['deep']['role'])+'</li>' for p in d['paragraphs'])+'</ol></section>'
    for p in d['paragraphs']:
        a = p['deep']
        body = bilingual(p) + '<div class="analysis"><h3>这段在说什么</h3>'+para(a['meaning'])+'<h3>在全文中的作用</h3>'+para(a['role'])+'<h3>与前后文的联系</h3>'+para(a['connection'])
        body += ''.join(disclosure(x['label'], para(x['text'])) for x in a['details'])
        body += disclosure('检查我的理解', para(a['question'])+'<textarea aria-label="我的理解" placeholder="先用自己的话回答；答案不会自动判分。"></textarea>'+disclosure('查看参考答案与核对点', para(a['answer'])))+'</div>'
        deep += unit('deep', p, body)
    l = d['language']
    language = '<section class="intro"><h2>借助中文，把原句读明白</h2>'+para(l['intro'])+'<p class="muted">先看帮助，再试着隐藏译文重读。无需强迫自己猜完所有生词。</p><h3>先认识这些词组</h3><div class="phrase-grid">'
    for x in l['phrases']:
        language += '<div class="phrase"><strong lang="en">'+e(x['text'])+'</strong>'+para(x['meaning'])+link(x['paragraph_id'])+disclosure('教学例句（AI 编写）',para(x['example'],'english')+para(x['example_translation']))+'</div>'
    language += '</div></section><h2>带着准备，阅读全文</h2>'
    language += ''.join(unit('language', p, bilingual(p)) for p in d['paragraphs'])
    language += '<section class="intro"><h2>精选原句：分块读，而非逐词猜</h2>'
    for s in l['sentences']:
        language += '<div class="sentence">'+link(s['paragraph_id'])+para(s['original'],'english')+'<div class="chunks">'+''.join('<div><span lang="en">'+e(ch['text'])+'</span><small>'+e(ch['meaning'])+'</small></div>' for ch in s['chunks'])+'</div>'+para(s['explanation'])+'</div>'
    language += '</section><section class="intro"><h2>试一试，再看答案</h2>'
    for i,q in enumerate(l['exercises']):
        language += '<div class="exercise">'+para(f'{i+1}. '+q['prompt'])+link(q['paragraph_id'])
        if q['type'] == 'choice':
            language += '<fieldset><legend>选择你的答案</legend>'+''.join(f'<label><input type="radio" name="q{i}"> {e(o)}</label>' for o in q['options'])+'</fieldset>'
        else:
            language += '<textarea aria-label="我的练习回答" placeholder="在这里写下你的回答"></textarea>'
        language += disclosure('查看答案与解释',para(q['answer'])+para(q['explanation']))+'</div>'
    language += '<h3>明天先回忆，再回看</h3><ul>'+''.join('<li>'+e(r)+'</li>' for r in l['review'])+'</ul><p class="muted">练习输入仅保留在本次打开的页面中。重要回答可复制保存或带回对话讨论。</p></section>'
    nav = ''.join(link(p['id']) for p in d['paragraphs'])
    panels = ''.join(f'<section id="panel-{mode}" role="tabpanel" aria-labelledby="tab-{mode}" tabindex="0"'+(' hidden' if mode!='quick' else '')+'>'+content+'</section>' for mode,content in [('quick',quick),('deep',deep),('language',language)])
    # Escape '<' so article text cannot terminate the JSON script element.
    payload = json.dumps({'title':d['title'],'paragraphs':d['paragraphs']},ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template = (ROOT/'assets/reader.html').read_text()
    values = {'TITLE':e(d['title']), 'META':e(f"{d['author']} · {d['source']} · {d['source_date']}"), 'NAV':nav,'PANELS':panels,'DATA':payload,'CSS':(ROOT/'assets/reader.css').read_text(),'JS':(ROOT/'assets/reader.js').read_text()}
    # Single substitution avoids interpreting marker-like source text as template directives.
    import re
    return re.sub(r'@@(TITLE|META|NAV|PANELS|DATA|CSS|JS)@@',lambda m:values[m[1]],template)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    try:
        d=json.loads(args.input.read_text(encoding='utf-8'))
        errors=validate(d)
    except (ValueError,OSError) as exc:
        parser.exit(1,str(exc)+'\n')
    if errors: parser.exit(1,'\n'.join(errors)+'\n')
    if args.check:
        print(f'Validated {len(d["paragraphs"])} paragraphs and all three modes.'); return
    if not args.output: parser.error('--output is required unless --check')
    if args.output.exists(): parser.exit(1,'Output exists; choose a new version filename.\n')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(render(d),encoding='utf-8')
    print(args.output)

if __name__=='__main__': main()
