# Müəllif: Kamran Muradov
# Fayl: evaluate_model.py
# Məqsəd: Süni İntellekt (ML) modelinin performansını hesablamaq və hesabat çıxarmaq

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import time

print("⏳ 1. Məlumat bazası (tickets.csv) yüklənir...")
start_time = time.time()
# RAM-ı qorumaq üçün 1 milyonluq bazanın 100,000 sətirlik nümunəsini test edirik
df = pd.read_csv('data/tickets.csv').sample(n=100000, random_state=42)

print("⏳ 2. Süni İntellekt modeli (helpdesk_classifier_model.pkl) oxunur...")
model = joblib.load('helpdesk_classifier_model.pkl')

# Məlumatları Test və Təlim (Train/Test) hissələrinə bölürük (80% Təlim, 20% Test)
X = df['ticket_text']
y = df['category']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("🤖 3. Model test məlumatları üzərində imtahan edilir (Predict)...")
y_pred = model.predict(X_test)

# --- NƏTİCƏLƏRİN HESABLANMASI ---
accuracy = accuracy_score(y_test, y_pred)
print("\n" + "="*50)
print(f"🎯 ÜMUMİ DƏQİQLİK (ACCURACY): {accuracy * 100:.2f}%")
print("="*50)

print("\n📊 DETALLI HESABAT (Classification Report):\n")
print(classification_report(y_test, y_pred))
print(f"⏱️ Əməliyyat müddəti: {time.time() - start_time:.2f} saniyə")

# --- CONFUSION MATRIX (Xəta Matrisi) ÇƏKİLMƏSİ ---
print("\n🎨 Confusion Matrix (Xəta Matrisi) qrafiki hazırlanır...")
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=model.classes_, yticklabels=model.classes_)
plt.title('ASOIU Helpdesk AI - Confusion Matrix (Xəta Matrisi)', fontsize=15)
plt.xlabel('AI-nin Təxmin Etdiyi Şöbə', fontsize=12)
plt.ylabel('Əsl (Real) Şöbə', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()

# Qrafiki kompüterə şəkil kimi yadda saxlayır
plt.savefig('AI_Performans_Qrafiki.png', dpi=300)
print("✅ Qrafik 'AI_Performans_Qrafiki.png' adı ilə yadda saxlanıldı!")
plt.show()
