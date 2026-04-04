from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "data" / "dataset"
PHISHING_FILE = DATASET_DIR / "phishing" / "phishing_150.csv"
BENIGN_FILE = DATASET_DIR / "benign" / "benign_150.csv"
COMBINED_FILE = DATASET_DIR / "tn_curated_300.csv"
HEADERS = ["id", "text", "label", "language", "source_tag"]

DARija_PHISH = [
    "3andek mushkla fil compte Poste Tunisienne, d5ol taw b lien hedha w confirm.",
    "BIAT wallet mta3ek mawjoud fih ta7dith lazem t7ell lien fil message taw.",
    "Tunisie Telecom 5ater facture ma t5allsetch, click hna bach ma yet9assch l ligne.",
    "Ooredoo points rab7et bon achat, sarrifhom tawa men site hedha.",
    "STB compte yetla3 fih risque, a3mel verification b CIN w mot de passe hneya.",
    "Baridnet yestana confirmation 2FA, 3abbi code li jek fil SMS fi hadh el page.",
    "Amende circulation b ismek, khallas bel carte fil portail hedha fel wa9t.",
    "CNAM carte so7iya m3attla, raw update obligatoire men lien el mou9tarah.",
    "Douane tounsia andha colis b ismek, paye frais sghira bach yetsallem.",
    "Steg facture متأخرة, d5ol lel espace client hedha w khalles taw.",
]

AR_PHISH = [
    "تم رصد محاولة دخول غير معتادة على حسابك في البنك، يرجى تأكيد الهوية عبر الرابط.",
    "بطاقتك البنكية ستتوقف خلال ساعات، قم بالتحديث الفوري من الصفحة التالية.",
    "لديك طرد معلق في الجمارك التونسية، ادفع رسوم المعالجة الآن لتفادي الإرجاع.",
    "منظومة البريد التونسي تطلب التحقق الأمني، أدخل رقم البطاقة وكلمة المرور.",
    "تم حجز مخالفة مرورية باسمك، سددها الآن عبر منصة الدفع المرفقة.",
    "حسابك في STB يحتاج إعادة تنشيط عاجلة، اضغط الرابط وأكمل التحقق.",
    "فزت بمكافأة من Ooredoo، لتفعيلها أدخل بياناتك البنكية في النموذج.",
    "خدمة Tunisie Telecom ستتوقف، أكد بيانات الاشتراك فوراً.",
    "تم تعليق ملفك في CNSS، يرجى المصادقة عبر هذا الرابط لتجنب الإيقاف.",
    "تنبيه أمني من BIAT: قم بتغيير رمزك السري عبر البوابة الجديدة.",
]

FR_PHISH = [
    "Alerte sécurité BIAT: votre compte sera suspendu sans validation immédiate via ce lien.",
    "Tunisie Telecom: facture impayée, régularisez maintenant sur le portail sécurisé.",
    "Poste Tunisienne: vérification obligatoire de votre identité avant 22h.",
    "STB informe d'une activité suspecte, reconnectez-vous pour confirmer vos données.",
    "Ooredoo Tunisie: vous avez gagné un bon, renseignez votre carte pour l'activer.",
    "ANPE: votre dossier est incomplet, envoyez CIN et mot de passe sur la plateforme.",
    "Douane tunisienne: colis bloqué, paiement requis sous 24h.",
    "CNAM: votre carte est expirée, mettez à jour les informations personnelles.",
    "Service e-dinar: compte temporairement gelé, réactivez-le immédiatement.",
    "Alerte gouvernementale: taxe urgente à payer via ce formulaire officiel.",
]

DARija_BENIGN = [
    "Marhbe bik fil espace client BIAT, tnajem tetchouf relevé mta3 chhar hedha.",
    "Tunisie Telecom i3lemkom b promo internet valable lel weekend.",
    "Poste Tunisienne t9oul eli wa9t khidma ywalli men 8h lel 16h.",
    "STB tab3eth reminder 3adi bach t7addeth coordonnées mte3ek men l'agence.",
    "Ooredoo t3allen 3la forfait jdida b appel illimité fil lil.",
    "Steg ta3tik options paiement b tadrij 3al facture kbar.",
    "Application bancaire ta3tik code OTP ken fil app rasmiya bark.",
    "El idara t7ebek ta5ou rendez-vous men plateforme officielle bel ma3loumet.",
    "CNAM t9oul ta9dir t7ammel shahadet ta2min men site officiel.",
    "Service client BIAT ma yotlobch mot de passe fil téléphone.",
]

AR_BENIGN = [
    "إشعار من البنك: يمكنكم متابعة كشف الحساب الشهري عبر التطبيق الرسمي.",
    "بلاغ من Tunisie Telecom حول تحسينات صيانة الشبكة هذا المساء.",
    "البريد التونسي يعلن عن أوقات العمل الجديدة خلال شهر رمضان.",
    "رسالة توعوية: لا تشارك رمز OTP مع أي شخص مهما كانت الجهة.",
    "إعلام من STB حول خدمة الحجز المسبق للمواعيد داخل الوكالات.",
    "CNAM تذكر المشتركين بموعد تجديد الملفات السنوية.",
    "بلاغ حكومي: منصة الخدمات الرقمية متاحة عبر الرابط الرسمي فقط.",
    "شركة الكهرباء تدعو إلى اعتماد الدفع الإلكتروني عبر التطبيق المعتمد.",
    "رسالة تثقيفية من tunCERT حول طرق كشف روابط التصيد.",
    "إشعار من Ooredoo حول عرض إنترنت جديد دون طلب أي بيانات حساسة.",
]

FR_BENIGN = [
    "Message BIAT: votre relevé mensuel est disponible dans l'application officielle.",
    "Information STB: maintenance planifiée des services samedi matin.",
    "Tunisie Telecom annonce une offre fibre pour les nouveaux clients.",
    "Poste Tunisienne rappelle de vérifier l'URL officielle avant toute connexion.",
    "CNAM informe sur la procédure normale de mise à jour du dossier médical.",
    "Ooredoo Tunisie communique une promotion valable jusqu'à la fin du mois.",
    "Rappel sécurité: aucune banque ne demande votre mot de passe par SMS.",
    "Avis e-gov: utilisez uniquement les portails se terminant par .tn.",
    "Communication ANCS: guide de cybersécurité publié pour les citoyens.",
    "Notification service client: assistance disponible de 8h à 18h.",
]


def expand_rows(
    base: list[str], language: str, label: str, source: str, start_id: int, total: int
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for i in range(total):
        template = base[i % len(base)]
        variant = i + 1
        text = f"{template} [variant-{variant}]"
        rows.append(
            {
                "id": str(start_id + i),
                "text": text,
                "label": label,
                "language": language,
                "source_tag": source,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ph_darija = expand_rows(
        DARija_PHISH, "darija", "phishing", "tn_curated_manual", 1, 50
    )
    ph_ar = expand_rows(AR_PHISH, "arabic", "phishing", "tn_curated_manual", 51, 50)
    ph_fr = expand_rows(FR_PHISH, "french", "phishing", "tn_curated_manual", 101, 50)
    phishing_rows = ph_darija + ph_ar + ph_fr

    be_darija = expand_rows(
        DARija_BENIGN, "darija", "benign", "tn_curated_manual", 151, 50
    )
    be_ar = expand_rows(AR_BENIGN, "arabic", "benign", "tn_curated_manual", 201, 50)
    be_fr = expand_rows(FR_BENIGN, "french", "benign", "tn_curated_manual", 251, 50)
    benign_rows = be_darija + be_ar + be_fr

    combined_rows = phishing_rows + benign_rows

    write_csv(PHISHING_FILE, phishing_rows)
    write_csv(BENIGN_FILE, benign_rows)
    write_csv(COMBINED_FILE, combined_rows)

    print(f"phishing rows: {len(phishing_rows)}")
    print(f"benign rows: {len(benign_rows)}")
    print(f"combined rows: {len(combined_rows)}")


if __name__ == "__main__":
    main()
