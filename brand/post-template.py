import json,base64,subprocess,os
S='/tmp/claude-0/-home-claude/9303ba6b-f6c9-5cfb-9455-fe8fa012402d/scratchpad/'
IMG=S+'site/img/'
def b64(f):return 'data:image/jpeg;base64,'+base64.b64encode(open(IMG+f,'rb').read()).decode()
P=[
 dict(date='2026-11-08',kind='טיפ השבוע',title='כמה זמן כל מזון "עובד" בשבילכם?',
  body='נוזלים עוזבים את הקיבה תוך 0–20 דקות, פחמימות פשוטות תוך 20–40 דקות, חלבונים רזים תוך 1.5–3 שעות, וחלבון מוצק ושומנים בריאים תוך 4–6 שעות. זו "אדריכלות השובע": מי שמכיר את ציר הזמן הזה בונה ארוחות ששומרות עליו שבע.',
  ctaTop='רוצים להעמיק?',ctaName='הספר "קצר ולעניין"',ctaSub='לפרטים ולרכישה: barilifestyle.com',cover='peek-book1.jpg',shape='book'),
 dict(date='2026-11-15',kind='ליווי 360°',title='להגיע לוועדה מוכנים ובטוחים',
  body='מעטפת אישית לפני הניתוח ואחריו: סדר ובהירות מול הבדיקות והמסמכים, הכנה מנטלית להערכת העובדת הסוציאלית ולוועדה, וכלים לשמור על ההישגים גם הרבה אחרי הניתוח.',
  ctaTop='שיחה ראשונה – בלי התחייבות',ctaName='שיחת התאמה',ctaSub='052-6369991 · barilifestyle.com',cover='hero-halo.jpg',shape='round'),
 dict(date='2026-11-22',kind='טיפ השבוע',title='של מי הקול הזה?',
  body='"אני עצלן", "אני לא מסוגל להתמיד". רשמו מחשבה כזו ושאלו: של מי הקול הזה? מאיפה למדתי אותו? האם זה באמת נכון? זה הכלי "אני זה לא המחשבות שלי" – הצעד הראשון לערער על הקול הפנימי.',
  ctaTop='רוצים להעמיק?',ctaName='ערכת האימון לחוסן מנטלי',ctaSub='לפרטים ולרכישה: barilifestyle.com',cover='peek-kit.jpg',shape='book'),
 dict(date='2026-11-29',kind='מהמדף שלנו',title='המצפן לאריכות ימים',
  body='המדריך לעיצוב רווחת בריאות על פי שיטת BariMF: שינוי תודעה התנהגותי שמחבר את הגוף, הנפש וההרגלים לדרך אחת – ארוכה ובריאה.',
  ctaTop='הספר של עופר לקסמן',ctaName='המצפן לאריכות ימים',ctaSub='לפרטים ולרכישה: barilifestyle.com',cover='peek-book2.jpg',shape='book'),
]
TPL='''<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
html{overflow:hidden;width:1080px;height:1350px}
body{position:relative;width:1080px;height:1350px;overflow:hidden;font-family:"Liberation Sans","DejaVu Sans",sans-serif;color:#22313A;
 background:radial-gradient(70% 50% at 100% 0%,rgba(184,146,90,.22),transparent 60%),radial-gradient(60% 45% at 0% 100%,rgba(122,143,110,.22),transparent 65%),linear-gradient(160deg,#FFFDF8,#EFE7D6)}
.bar{height:18px;background:linear-gradient(90deg,#1E4A55,#5E7A55 55%,#B8925A)}
.ring{position:absolute;border-radius:50%;border:2px solid rgba(184,146,90,.35)}
.top{display:flex;justify-content:space-between;align-items:center;padding:64px 90px 0}
.pill{font-size:34px;font-weight:700;color:#fff;padding:14px 30px;border-radius:999px;background:linear-gradient(90deg,#B8925A,#8E6E3E)}
.logo{background:#fff;border-radius:22px;padding:12px 16px;box-shadow:0 10px 30px rgba(30,74,85,.15)}
.logo img{height:96px;display:block}
h1{padding:70px 90px 0;font-size:84px;line-height:1.12;color:#1E4A55;font-weight:700;letter-spacing:-.5px}
.line{margin:34px 90px 0;width:120px;height:8px;border-radius:8px;background:linear-gradient(90deg,#B8925A,#7A8F6E)}
p.body{padding:38px 90px 0;font-size:41px;line-height:1.62;color:#2a3a40}
.cta{position:absolute;left:70px;right:70px;bottom:150px;height:250px;border-radius:40px;display:flex;align-items:center;gap:40px;padding:0 54px 0 0;
 background:linear-gradient(115deg,#1E4A55,#2C5B58 55%,#5E7A55);box-shadow:0 30px 60px rgba(30,74,85,.3);color:#fff}
.cta .t{flex:1}
.cta .a{font-size:32px;color:#F3DDB0;font-weight:700}
.cta .b{font-size:52px;font-weight:700;margin-top:8px;line-height:1.15}
.cta .c{font-size:30px;opacity:.88;margin-top:12px}
.cover{flex:none;margin-left:50px}
.cover.book img{height:290px;transform:rotate(-7deg) translateY(-24px);border-radius:4px 12px 12px 4px;box-shadow:-5px 5px 0 #F6F1E6,-10px 10px 0 #E4DCCB,0 26px 50px rgba(0,0,0,.4)}
.cover.round img{width:250px;height:250px;object-fit:cover;border-radius:50%;border:8px solid #F3DDB0;transform:translateY(-34px);box-shadow:0 26px 50px rgba(0,0,0,.35)}
.foot{position:absolute;left:90px;right:90px;bottom:62px;display:flex;justify-content:space-between;font-size:30px;color:#5b6b70}
.foot b{color:#1E4A55}
</style></head><body>
<div class="bar"></div>
<div class="ring" style="width:620px;height:620px;left:-260px;bottom:240px"></div>
<div class="ring" style="width:820px;height:820px;left:-360px;bottom:140px;border-color:rgba(122,143,110,.2)"></div>
<div class="top"><span class="pill">{kind}</span><span class="logo"><img src="{logo}"></span></div>
<h1>{title}</h1><div class="line"></div>
<p class="body">{body}</p>
<div class="cta"><div class="t"><div class="a">{ctaTop}</div><div class="b">{ctaName}</div><div class="c">{ctaSub}</div></div><div class="cover {shape}"><img src="{cover}"></div></div>
<div class="foot"><span><b>אתי ועופר לקסמן</b> · שיטת BariMF</span><span dir="ltr">barilifestyle.com</span></div>
</body></html>'''
os.makedirs(S+'posts/out',exist_ok=True)
logo=b64('logo.jpg')
for p in P:
    h=TPL
    for k,v in dict(p,logo=logo,cover=b64(p['cover'])).items():h=h.replace('{'+k+'}',v)
    open(S+'posts/out/%s.html'%p['date'],'w',encoding='utf-8').write(h)
json.dump(P,open(S+'posts/plan.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
