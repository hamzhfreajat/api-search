import re
from typing import Dict, List, Set, Tuple, Optional
from pydantic import BaseModel

class SearchIntent(BaseModel):
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = []
    confidence: float = 0.0
    clean_query: str = ""

def _n(s: str) -> str:
    if not s: return s
    for a, b in [('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ة', 'ه'), ('ى', 'ي')]:
        s = s.replace(a, b)
    return s.strip()

def _strip_diacritics(s: str) -> str:
    return re.sub(r'[\u064B-\u065F\u0670]', '', s)

_sale_signals = set(_n(w) for w in [
    'للبيع', 'بيع', 'لبيع', 'نبيع', 'تمليك', 'تملك', 'منتهي بالتمليك', 'منتهيه بالتمليك',
    'ايجار منتهي بالتمليك', 'شراء', 'شري', 'تقسيط', 'اقساط', 'قسط', 'بالتقسيط', 'بالاقساط', 'بالقسط',
    'بدون مقدم', 'بدون فوايد', 'بدون فواید', 'للتنازل', 'تنازل', 'للبيع بالتقسيط'
])

_rent_signals = set(_n(w) for w in [
    'للايجار', 'للإيجار', 'للاجار', 'للاجاره', 'للاجره', 'ايجار', 'إيجار', 'اجار', 'اجاره',
    'ايجارات', 'تاجير', 'تأجير', 'ايجار يومي', 'ايجار شهري', 'ايجار سنوي', 'ايجار جديد', 'ايجار قديم',
    'قانون جديد', 'قانون قديم', 'يومي', 'شهري', 'سنوي', 'اسبوعي', 'بالساعه', 'بالساعة', 'بالشهر',
    'يوم واحد'
])

_strong_land_signals = set(_n(w) for w in [
    'ارض', 'اراضي', 'أراضي', 'أرض', 'اراضى', 'قطعه ارض', 'قطعة ارض', 'قطع اراضي', 'قطعة أرض',
    'نص ارض', 'الارض', 'ارض زراعيه', 'ارض صناعيه', 'ارض تجاريه', 'اراضي زراعيه', 'اراضي صناعيه', 'اراضي تجاريه',
    'ارض زراعية', 'ارض صناعية', 'ارض تجارية', 'اراضي زراعية', 'اراضي صناعية', 'اراضي تجارية',
    'حراج اراضي', 'بيع اراضي', 'اراضي للبيع', 'مزرعه', 'مزرعة', 'مزارع', 'فدان', 'قيراط',
    'ارض خام', 'ارض فضاء', 'تقسيط اراضي', 'شراء اراضي', 'اراضي للايجار', 'ارض للايجار',
    'ارض استثماريه', 'اراضي استثماريه', 'ارض سكنيه', 'أرض سكنية', 'تثمين اراضي', 'تثمين أراضي',
    'مخطط', 'اسعار اراضي', 'اسعار الاراضي', 'بيع ارض', 'عقار اراضي', 'عقار ارض', 'سمسار اراضي',
    'مكتب بيع اراضي', 'مواقع بيع اراضي', 'موقع اراضي', 'موقع بيع اراضي', 'موقع حراج اراضي', 'موقع لبيع الاراضي',
    'حراج الاراضي', 'صور اراضي للبيع', 'عرض ارض للبيع', 'اعلان ارض للبيع', 'اعلان قطعة ارض', 'لبيع الاراضي',
    'قطع اراضي زراعيه', 'قطع اراضي للبيع', 'قطعه ارض زراعيه', 'قطعة ارض للايجار', 'سعر الاراضي', 'سعر الفدان', 'سعر قيراط',
    'اراضي وعقارات'
])

_property_type_map = {
    'شقق سكنيه': 'شقة', 'شقق سكنية': 'شقة', 'شقه فندقيه': 'شقة فندقية', 'شقة فندقيه': 'شقة فندقية',
    'شقق فندقيه': 'شقة فندقية', 'شقة فندقية': 'شقة فندقية', 'شقق فندقية': 'شقة فندقية',
    'شقه ارضيه': 'شقة أرضية', 'شقة ارضيه': 'شقة أرضية', 'شقة ارضية': 'شقة أرضية', 'شقة استوديو': 'شقة',
    'غرفة استوديو': 'شقة', 'شقق روف': 'روف', 'شقة روف': 'روف', 'شقق': 'شقة', 'شقه': 'شقة', 'شقة': 'شقة',
    'استوديو': 'ستوديو', 'ستوديو': 'ستوديو', 'استديو': 'ستوديو', 'استديوهات': 'ستوديو',
    'غرفتين وصاله': 'غرفتين وصالة', 'غرفه وصاله': 'غرفة وصالة', 'غرفة وصاله': 'غرفة وصالة', 'غرفة وصالة': 'غرفة وصالة',
    'غرفه وحمام': 'غرفة', 'غرفة وحمام': 'غرفة', 'غرفة ومطبخ': 'غرفة', 'غرفه ماستر': 'غرفة', 'غرفة ماستر': 'غرفة',
    'غرفه': 'غرفة', 'غرفة': 'غرفة', 'غرف': 'غرفة', 'سرير': 'سرير', 'سكن عمال': 'سكن', 'سكن مشترك': 'سكن', 'سكن': 'سكن',
    'روف': 'روف', 'طابق كامل': 'طابق كامل', 'طابق': 'طابق كامل', 'دوبلكس': 'دوبلكس', 'بنتهاوس': 'دوبلكس',
    'فيلا صغيره': 'فيلا', 'فيلا': 'فيلا', 'فله': 'فيلا', 'فلل': 'فيلا', 'قصر': 'فيلا',
    'بيت شعبي': 'بيت', 'بيت ارضي': 'بيت', 'بيوت جاهزه': 'بيت', 'بيوت جاهزة': 'بيت', 'بيت كبير': 'بيت',
    'بيت': 'بيت', 'بيوت': 'بيت', 'منزل مستقل': 'بيت', 'منزل': 'بيت', 'منازل': 'بيت', 'دور': 'دور',
    'عماره': 'عمارة', 'عمارة': 'عمارة', 'شاليهات': 'شاليه', 'شاليه': 'شاليه', 'مخيم': 'مخيم',
    'كرفان': 'كرفان', 'كرفانات': 'كرفان', 'كوخ': 'كوخ', 'استراحه': 'استراحة', 'استراحة': 'استراحة',
    'محلات تجاريه': 'محل تجاري', 'محل تجاري': 'محل تجاري', 'محلات': 'محل تجاري', 'محل': 'محل تجاري',
    'مكاتب': 'مكتب', 'مكتب': 'مكتب', 'عياده': 'عيادة', 'عيادة': 'عيادة', 'مصنع': 'مصنع', 'مشاريع': 'مشروع', 'مشروع': 'مشروع',
    'جاخور': 'جاخور', 'حوش': 'حوش', 'بوشملان': 'بوشملان', 'بو شملان': 'بوشملان', 'ابو شملان': 'بوشملان',
    'قطعه ارض': 'أرض', 'قطعة ارض': 'أرض', 'قطع اراضي': 'أرض', 'نص ارض': 'أرض', 'ارض زراعيه': 'أرض زراعية',
    'ارض صناعيه': 'أرض صناعية', 'ارض تجاريه': 'أرض تجارية', 'ارض خام': 'أرض', 'ارض فضاء': 'أرض',
    'ارض سكنيه': 'أرض سكنية', 'ارض استثماريه': 'أرض', 'ارض': 'أرض', 'اراضي': 'أرض', 'مزرعه': 'مزرعة', 'مزرعة': 'مزرعة', 'مزارع': 'مزرعة',
}
_property_type_values = set(_property_type_map.values())

_furnishing_map = {
    'مفروشه': 'furnished:مفروشة', 'مفروشة': 'furnished:مفروشة', 'مفرشه': 'furnished:مفروشة', 'مفرشة': 'furnished:مفروشة',
    'مفروش': 'furnished:مفروشة', 'مؤثثه': 'furnished:مفروشة', 'مؤثثة': 'furnished:مفروشة', 'مؤثث': 'furnished:مفروشة',
    'غير مفروشه': 'furnished:غير مفروشة', 'غير مفروشة': 'furnished:غير مفروشة', 'بدون فرش': 'furnished:غير مفروشة',
}

_bedrooms_map = {
    'ستوديو': 'bedrooms:ستوديو', 'غرفة وحدة': 'bedrooms:1', 'غرفة واحدة': 'bedrooms:1',
    'غرفتين': 'bedrooms:2', 'غرفتان': 'bedrooms:2', '3 غرف': 'bedrooms:3', 'ثلاث غرف': 'bedrooms:3', 'ثلاثة غرف': 'bedrooms:3',
    '4 غرف': 'bedrooms:4', 'اربع غرف': 'bedrooms:4', 'أربع غرف': 'bedrooms:4', '5 غرف': 'bedrooms:5', 'خمس غرف': 'bedrooms:5',
    '6 غرف': 'bedrooms:+6', 'ست غرف': 'bedrooms:+6', '7 غرف': 'bedrooms:+6', 'سبع غرف': 'bedrooms:+6',
    '8 غرف': 'bedrooms:+6', 'ثمان غرف': 'bedrooms:+6',
}

_bathrooms_map = {
    'حمام واحد': 'bathrooms:1', 'حمام': 'bathrooms:1', 'حمامين': 'bathrooms:2', 'حمامان': 'bathrooms:2',
    '3 حمامات': 'bathrooms:3', 'ثلاث حمامات': 'bathrooms:3', '4 حمامات': 'bathrooms:4', 'اربع حمامات': 'bathrooms:4', 'أربع حمامات': 'bathrooms:4',
    '5 حمامات': 'bathrooms:5', 'خمس حمامات': 'bathrooms:5',
}

_floor_map = {
    'تسوية': 'تسوية', 'التسوية': 'تسوية', 'طابق التسوية': 'تسوية',
    'شبه ارضي': 'تسوية', 'شبة ارضي': 'تسوية', 'طابق شبه ارضي': 'تسوية',
    'الطابق الأرضي': 'طابق أرضي', 'ارضي': 'طابق أرضي', 'طابق ارضي': 'طابق أرضي',
    'الطابق الاول': 'طوابق علوية', 'طابق اول': 'طوابق علوية', 'الاول': 'طوابق علوية', 'الطابق الثاني': 'طوابق علوية', 'طابق ثاني': 'طوابق علوية', 'الثاني': 'طوابق علوية',
    'الطابق الثالث': 'طوابق علوية', 'طابق ثالث': 'طوابق علوية', 'الثالث': 'طوابق علوية', 'الطابق الرابع': 'طوابق علوية', 'طابق رابع': 'طوابق علوية', 'الرابع': 'طوابق علوية',
    'الطابق الخامس': 'طوابق علوية', 'طابق خامس': 'طوابق علوية', 'الخامس': 'طوابق علوية', 'الطابق السادس': 'طوابق علوية', 'طابق سادس': 'طوابق علوية', 'السادس': 'طوابق علوية',
    'الطابق السابع': 'طوابق علوية', 'طابق سابع': 'طوابق علوية', 'السابع': 'طوابق علوية',
}

_age_map = {
    'جديد': 'age:0 - 1 سنة', 'جديده': 'age:0 - 1 سنة', 'جديدة': 'age:0 - 1 سنة', 'قيد الانشاء': 'age:0 - 1 سنة', 'تحت الانشاء': 'age:0 - 1 سنة',
    'عمر سنة': 'age:0 - 1 سنة', 'عمر سنه': 'age:0 - 1 سنة', 'عمر سنتين': 'age:1 - 5 سنوات', 'عمر 2': 'age:1 - 5 سنوات', 'عمر 3': 'age:1 - 5 سنوات',
    'عمر 4': 'age:1 - 5 سنوات', 'عمر 5': 'age:1 - 5 سنوات', '5 سنوات': 'age:1 - 5 سنوات', 'عمر 6': 'age:5 - 10 سنوات', 'عمر 7': 'age:5 - 10 سنوات',
    'عمر 8': 'age:5 - 10 سنوات', 'عمر 9': 'age:5 - 10 سنوات', 'عمر 10': 'age:5 - 10 سنوات', '10 سنوات': 'age:5 - 10 سنوات',
    'عمر 11': 'age:10 - 19 سنة', 'عمر 12': 'age:10 - 19 سنة', 'عمر 15': 'age:10 - 19 سنة', 'عمر 20': 'age:20+ سنة', 'قديم': 'age:20+ سنة',
}

_rent_period_map = {
    'يوم واحد': 'rent_duration:يومي', 'يومي': 'rent_duration:يومي', 'اليومي': 'rent_duration:يومي',
    'بالساعه': 'rent_duration:يومي', 'بالساعة': 'rent_duration:يومي', 'سياحي': 'rent_duration:يومي',
    'شهري': 'rent_duration:شهري', 'الشهري': 'rent_duration:شهري', 'بالشهر': 'rent_duration:شهري', 'شهر': 'rent_duration:شهري',
    'سنوي': 'rent_duration:سنوي', 'السنوي': 'rent_duration:سنوي', 'سنه': 'rent_duration:سنوي', 'سنة': 'rent_duration:سنوي',
    'اسبوعي': 'rent_duration:اسبوعي',
}

_payment_map = {
    'بالتقسيط بدون مقدم': 'تقسيط', 'بالتقسيط بدون فوايد': 'تقسيط', 'تقسيط بدون مقدم': 'تقسيط',
    'تقسيط بدون فوايد': 'تقسيط', 'تقسيط': 'تقسيط', 'بالتقسيط': 'تقسيط',
    'اقساط': 'أقساط', 'بالاقساط': 'أقساط', 'بالقسط': 'أقساط', 'قسط': 'أقساط',
    'كاش': 'كاش', 'نقدا': 'كاش', 'كاش واقساط': 'كاش أو أقساط',
}

_tenant_map = {
    'عزاب': 'عزاب', 'عزوبيه': 'عزاب', 'للشباب': 'طلاب', 'عائلات': 'عائلات', 'عائلي': 'عائلات', 'العائلي': 'عائلات',
    'عائله': 'عائلات', 'عائلة': 'عائلات', 'عمال': 'سكن موظفين', 'للعمال': 'سكن موظفين',
}

_source_map = {
    'من المالك مباشره': 'من المالك', 'من المالك مباشرة': 'من المالك', 'من المالك': 'من المالك',
    'مباشره': 'من المالك', 'بدون عموله': 'من المالك', 'بدون عمولة': 'من المالك',
}

_features_map = {
    'بحمام سباحه': 'extra_features:مسبح', 'بحمام سباحة': 'extra_features:مسبح', 'حمام سباحه': 'extra_features:مسبح',
    'حمام سباحة': 'extra_features:مسبح', 'مسبح': 'extra_features:مسبح', 'دوبلكس': 'geometric_shape:دوبلكس',
    'دبلكس': 'geometric_shape:دوبلكس', 'دورين': 'geometric_shape:دوبلكس', 'روف': 'geometric_shape:روف',
    'ملحق': 'geometric_shape:روف', 'ارضي': 'floor:أرضي', 'ارضيه': 'floor:أرضي', 'أرضية': 'floor:أرضي',
    'سرداب': 'floor:تسوية', 'حوش': 'extra_features:حوش', 'على البحر': 'extra_features:إطلالة على البحر', 'علي البحر': 'extra_features:إطلالة على البحر',
}

_project_map = {
    'بيت الوطن': 'بيت الوطن', 'القوات المسلحه': 'القوات المسلحة', 'التوسعات الشماليه': 'التوسعات الشمالية',
    'العلمين الجديده': 'العلمين الجديدة', 'النزهه الجديده': 'النزهة الجديدة', 'كمبوند بادية': 'بادية',
    'كمبوند ارمونيا': 'أرمونيا', 'كمبوند الياسمين': 'الياسمين', 'كمبوند لوروا': 'لوروا', 'كمبوند ديار': 'ديار',
    'كمبوند ريتاج': 'ريتاج', 'كمبوند زايد ديونز': 'زايد ديونز', 'كمبوند روضه السالميه': 'روضة السالمية',
    'كومباوند البروج': 'البروج', 'كومباوند انطونيادس': 'انطونيادس', 'جولدن جيتس': 'جولدن جيتس', 'روضه السالميه': 'روضة السالمية',
    'زايد ديونز': 'زايد ديونز', 'درب الحرمين': 'درب الحرمين', 'داماك': 'داماك', 'ارمونيا': 'أرمونيا', 'الياسمين': 'الياسمين',
    'البروج': 'البروج', 'ديار': 'ديار', 'بادية': 'بادية', 'روشن': 'روشن', 'مدينتي': 'مدينتي', 'المدينه': 'مدينتي',
    'العلمين': 'العلمين الجديدة', 'لوروا': 'لوروا', 'نيوم': 'نيوم', 'ريتاج': 'ريتاج', 'ريف المصري': 'الريف المصري',
    'الوفاء': 'الوفاء', 'الاوقاف': 'الأوقاف', 'العجلان': 'العجلان', 'المراسم': 'المراسم', 'انطونيادس': 'انطونيادس',
    'شموع العقار': 'شموع العقار', 'اسس العقار': 'أسس العقار', 'سهيل العقاريه': 'سهيل', 'سهيل عقار': 'سهيل',
    'الغرير للعقارات': 'الغرير', 'ابو شملان للعقارات': 'بوشملان', 'بو شملان للعقارات': 'بوشملان', 'بوشملان عقار': 'بوشملان',
    'ديار العقاريه': 'ديار',
}

def _extract_location(query: str, cities: List[dict]) -> Tuple[Optional[str], str]:
    best_loc = None
    best_match_len = -1
    clean_query = f" {query} "
    
    for city in cities:
        name_ar = _n(city['name_ar'])
        target = f" {name_ar} "
        if target in clean_query and len(name_ar) > best_match_len:
            best_loc = city['name_ar']
            best_match_len = len(name_ar)
            
        for region in city.get('regions', []):
            r_name = _n(region['name_ar'])
            target = f" {r_name} "
            if target in clean_query and len(r_name) > best_match_len:
                best_loc = region['name_ar']
                best_match_len = len(r_name)
                
    if best_loc:
        normalized_loc = _n(best_loc)
        clean_query = clean_query.replace(f" {normalized_loc} ", " ")
        
    return best_loc, clean_query.strip()

def _extract_multi_word_matches(dict_map: Dict[str, str], padded_query: str, tags: Set[str]) -> str:
    sorted_keys = sorted(dict_map.keys(), key=len, reverse=True)
    for k in sorted_keys:
        nk = _n(k)
        if f" {nk} " in padded_query:
            tags.add(dict_map[k])
            padded_query = padded_query.replace(f" {nk} ", " ")
    return padded_query

def _score_signals(padded_query: str, signals: Set[str]) -> int:
    score = 0
    words = padded_query.split()
    for s in signals:
        if ' ' in s:
            if f" {s} " in padded_query:
                score += 1
        else:
            if s in words:
                score += 1
    return score

def _has_any_signal(padded_query: str, signals: Set[str]) -> bool:
    return _score_signals(padded_query, signals) > 0


def _apply_dynamic_regex(padded: str, tags: set) -> str:
    import re
    
    # 1. Area Extraction
    m_area = re.search(r'(?:مساح(?:ة|ه)|مساحته|بمساح(?:ة|ه))\s*(?:من|بين)?\s*(\d+)\s*(?:ال(?:ي|ى)|و)?\s*(\d+)?\s*(?:متر|م|مترمربع|متر مربع)?\s*(?:مربع)?', padded)
    if not m_area:
        m_area = re.search(r'(?<!\d)(?:من|بين)?\s*(\d+)\s*(?:ال(?:ي|ى)|و)?\s*(\d+)?\s*(?:متر|م|مترمربع|متر مربع)\s*(?:مربع)?', padded)
        
    if m_area:
        if m_area.group(2):
            tags.add(f"min_area:{m_area.group(1)}")
            tags.add(f"max_area:{m_area.group(2)}")
        else:
            tags.add(f"min_area:{m_area.group(1)}")
            tags.add(f"max_area:{m_area.group(1)}")
        padded = padded[:m_area.start()] + ' ' + padded[m_area.end():]

    # 2. Price Extraction
    m_price = re.search(r'(?:بسعر|ب|سعر|تحت|اقل من)\s*(?:من|بين)?\s*(\d+)\s*(الف|ألف)?\s*(?:ال(?:ي|ى)|و)?\s*(\d+)?\s*(الف|ألف)?\s*(?:دينار)?', padded)
    if not m_price:
        m_price = re.search(r'(?<!\d)(?:من|بين)?\s*(\d+)\s*(الف|ألف)?\s*(?:ال(?:ي|ى)|و)?\s*(\d+)?\s*(الف|ألف)?\s*(?:دينار)', padded)
    if not m_price:
        # Match 'من X الى Y' without keyword if numbers are large enough (> 100) or 'الف' is present
        m_price = re.search(r'(?<!\d)(?:من|بين)?\s*(\d+)\s*(الف|ألف)?\s*(?:ال(?:ي|ى)|و)\s*(\d+)\s*(الف|ألف)?\s*(?:دينار)?', padded)
    if not m_price:
        # Match 'X الف' or 'X دينار'
        m_price = re.search(r'(?<!\d)(\d+)\s*(الف|ألف|دينار)(?!\w)', padded)
        
    if m_price:
        # For the last fallback, it might have only group 1 and 2
        groups = m_price.groups()
        if len(groups) == 2:
            val = int(groups[0])
            if groups[1] in ['الف', 'ألف']: val *= 1000
            tags.add(f"min_price:{val}")
            tags.add(f"max_price:{val}")
        else:
            min_val = int(m_price.group(1))
            if m_price.group(2): min_val *= 1000
            
            if m_price.group(3):
                max_val = int(m_price.group(3))
                if m_price.group(4): max_val *= 1000
                tags.add(f"min_price:{min_val}")
                tags.add(f"max_price:{max_val}")
            else:
                tags.add(f"max_price:{min_val}")
        padded = padded[:m_price.start()] + ' ' + padded[m_price.end():]

    # 3. Floor Extraction
    m_floor = re.search(r'(?:الطابق|طابق|ط)\s*(الارضي|الاول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر|الاخير|\d+)', padded)
    if m_floor:
        val = m_floor.group(1)
        mapping = {'الارضي': '0', 'الاول': '1', 'الثاني': '2', 'الثالث': '3', 'الرابع': '4', 'الخامس': '5', 'السادس': '6', 'السابع': '7', 'الثامن': '8', 'التاسع': '9', 'العاشر': '10', 'الاخير': '99'}
        val = mapping.get(val, val)
        tags.add(f"floor:{val}")
        padded = padded[:m_floor.start()] + ' ' + padded[m_floor.end():]

    # 4. Bedrooms
    m_bed = re.search(r'(\d+)\s*(?:غرف(?:ة|ه)? نوم|غرف(?:ة|ه)?|نوم)', padded)
    if m_bed:
        val = int(m_bed.group(1))
        if val >= 6: tags.add("bedrooms:+6")
        else: tags.add(f"bedrooms:{val}")
        padded = padded[:m_bed.start()] + ' ' + padded[m_bed.end():]
        
    # 5. Bathrooms
    m_bath = re.search(r'(\d+)\s*(?:حمامات|حمام)', padded)
    if m_bath:
        tags.add(f"bathrooms:{m_bath.group(1)}")
        padded = padded[:m_bath.start()] + ' ' + padded[m_bath.end():]
        
    return padded

def _remove_stopwords(padded: str) -> str:
    import re
    stopwords = ['في', 'من', 'ب', 'عن', 'على', 'ل', 'الى', 'إلى', 'مع', 'و', 'او', 'أو', 'لل', 'اللي', 'الي']
    for word in stopwords:
        padded = re.sub(r'(?<!\S)' + word + r'(?!\S)', ' ', padded)
    return padded.strip()

class SearchIntentParser:
    @staticmethod
    def parse(raw_query: str, cities: List[dict] = []) -> SearchIntent:
        if not raw_query or not raw_query.strip():
            return SearchIntent(confidence=0)
            
        cleaned = _strip_diacritics(raw_query.strip())
        normalized = _n(cleaned)
        
        location, working_query = _extract_location(normalized, cities)
        
        tags = set()
        padded = f" {working_query} "
        import re as regex
        padded = regex.sub(r'[^\w\u0600-\u06FF]+', ' ', padded)
        
        padded = _apply_dynamic_regex(padded, tags)
        
        padded = _extract_multi_word_matches(_property_type_map, padded, tags)
        padded = _extract_multi_word_matches(_furnishing_map, padded, tags)
        padded = _extract_multi_word_matches(_bedrooms_map, padded, tags)
        padded = _extract_multi_word_matches(_bathrooms_map, padded, tags)
        padded = _extract_multi_word_matches(_floor_map, padded, tags)
        padded = _extract_multi_word_matches(_age_map, padded, tags)
        padded = _extract_multi_word_matches(_rent_period_map, padded, tags)
        padded = _extract_multi_word_matches(_payment_map, padded, tags)
        padded = _extract_multi_word_matches(_tenant_map, padded, tags)
        padded = _extract_multi_word_matches(_source_map, padded, tags)
        padded = _extract_multi_word_matches(_features_map, padded, tags)
        padded = _extract_multi_word_matches(_project_map, padded, tags)
        
        category_id = None
        category_name = None
        confidence = 0.5
        
        sale_score = _score_signals(padded, _sale_signals)
        rent_score = _score_signals(padded, _rent_signals)
        has_strong_land = _has_any_signal(padded, _strong_land_signals)
        
        if has_strong_land:
            category_id = 10313
            if sale_score > rent_score: category_name = 'أراضي للبيع'
            elif rent_score > sale_score: category_name = 'أراضي للإيجار'
            else: category_name = 'أراضي'
            confidence = 0.9
        elif sale_score > 0 and sale_score >= rent_score:
            if 'شقة' in tags or 'شقة أرضية' in tags: category_id, category_name = 10301, 'شقق للبيع'
            elif 'ستوديو' in tags: category_id, category_name = 10302, 'ستوديوهات للبيع'
            elif 'فيلا' in tags: category_id, category_name = 10101, 'فلل وقصور'
            elif 'بيت' in tags: category_id, category_name = 10102, 'بيوت مستقلة'
            elif 'دوبلكس' in tags: category_id, category_name = 10103, 'دوبلكس / بنتهاوس'
            elif 'عمارة' in tags: category_id, category_name = 10104, 'عمارة'
            elif 'طابق كامل' in tags: category_id, category_name = 10106, 'طابق كامل'
            elif 'روف' in tags: category_id, category_name = 10105, 'ملحق / روف'
            elif 'مزرعة' in tags: category_id, category_name = 10314, 'مزرعة'
            elif sale_score >= 2: category_id, category_name = 2, 'عقارات للبيع'
        elif rent_score > 0:
            if 'شقة' in tags or 'شقة أرضية' in tags: category_id, category_name = 301, 'شقق للإيجار'
            elif 'شقة فندقية' in tags: category_id, category_name = 303, 'شقق فندقية'
            elif 'ستوديو' in tags: category_id, category_name = 302, 'ستوديوهات للإيجار'
            elif 'فيلا' in tags: category_id, category_name = 304, 'فلل وقصور للإيجار'
            elif 'بيت' in tags: category_id, category_name = 305, 'بيوت مستقلة للإيجار'
            elif 'محل تجاري' in tags: category_id, category_name = 306, 'محل تجاري'
            elif 'مكتب' in tags: category_id, category_name = 307, 'مكاتب للإيجار'
            elif 'عيادة' in tags: category_id, category_name = 308, 'عيادات للإيجار'
            elif 'عمارة' in tags: category_id, category_name = 309, 'عمارة للإيجار'
            elif 'دور' in tags: category_id, category_name = 310, 'دور للإيجار'
            elif 'سكن' in tags: category_id, category_name = 311, 'سكن للإيجار'
            elif 'شاليه' in tags: category_id, category_name = 312, 'شاليهات ومصايف'
            elif 'مخيم' in tags: category_id, category_name = 313, 'مخيمات'
            elif 'استراحة' in tags: category_id, category_name = 315, 'استراحات'
            elif rent_score >= 2: category_id, category_name = 3, 'عقارات للإيجار'
            
        if category_id is not None:
            confidence += 0.4
            
        if category_id in [10301, 10302, 10101, 10102, 10103, 10104, 10106, 10105, 10314, 301, 303, 302, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 315]:
            tags = {t for t in tags if t not in _property_type_values}
            
        # Remove sale/rent signals from the clean query
        for s in _sale_signals.union(_rent_signals).union(_strong_land_signals):
            padded = padded.replace(f" {s} ", " ")
            
        # Remove stopwords from the clean query
        padded = _remove_stopwords(padded)
            
        return SearchIntent(
            category_id=category_id,
            category_name=category_name,
            location=location,
            tags=list(tags),
            confidence=min(confidence, 1.0),
            clean_query=padded.strip()
        )
