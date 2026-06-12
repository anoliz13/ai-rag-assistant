import asyncio
import uuid
from sqlalchemy import text
from app.core.database import async_session, init_db


SEED_DOCUMENTS = [
    {
        "filename": "Laporan Keuangan 2025.pdf",
        "file_type": "application/pdf",
        "content": """PT MAJU BERSAMA
LAPORAN KEUANGAN TAHUN 2025

IKHTISAR KEUANGAN
Total Pendapatan: Rp 2.500.000.000.000
Laba Bersih: Rp 375.000.000.000
Total Aset: Rp 5.200.000.000.000

SEGMEN BISNIS
1. Teknologi - Pendapatan Rp 1.200.000.000.000 (Pertumbuhan 45%)
2. Manufaktur - Pendapatan Rp 800.000.000.000 (Pertumbuhan 12%)
3. Jasa - Pendapatan Rp 500.000.000.000 (Pertumbuhan 28%)

ANALISIS PER KUARTAL 2025
Q1 2025: Pendapatan Rp 550M, Laba Bersih Rp 80M
Q2 2025: Pendapatan Rp 600M, Laba Bersih Rp 90M
Q3 2025: Pendapatan Rp 650M, Laba Bersih Rp 95M
Q4 2025: Pendapatan Rp 700M, Laba Bersih Rp 110M

PROYEKSI 2026
Target Pendapatan: Rp 3.200.000.000.000 (Pertumbuhan 28%)
Target Laba Bersih: Rp 500.000.000.000""",
    },
    {
        "filename": "Kebijakan Perusahaan.md",
        "file_type": "text/markdown",
        "content": """# Kebijakan Perusahaan PT Maju Bersama

## Jam Kerja
- Senin - Jumat: 08.00 - 17.00 WIB
- Istirahat: 12.00 - 13.00 WIB
- WFH: Maksimal 2 hari per minggu

## Cuti
- Cuti tahunan: 12 hari per tahun
- Cuti sakit: 14 hari per tahun (dengan surat dokter)
- Cuti melahirkan: 3 bulan
- Cuti pernikahan: 3 hari

## Tunjangan
- BPJS Kesehatan & Ketenagakerjaan
- Asuransi kesehatan tambahan (InHealth)
- Tunjangan transportasi: Rp 1.000.000/bulan
- Tunjangan makan: Rp 600.000/bulan
- Bonus tahunan: 1-3 kali gaji (berdasarkan performa)

## Aturan Penggunaan AI
Karyawan diperbolehkan menggunakan AI tools untuk meningkatkan produktivitas.
Dilarang memasukkan data rahasia perusahaan ke AI publik.
Semua output AI harus direview manusia sebelum dipublikasikan.""",
    },
]


async def seed():
    await init_db()
    async with async_session() as db:
        for doc in SEED_DOCUMENTS:
            doc_id = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO documents (id, filename, file_type, file_size, file_path, status, chunk_count)
                VALUES (:id, :filename, :file_type, :file_size, :file_path, :status, :chunk_count)
            """), {
                "id": doc_id,
                "filename": doc["filename"],
                "file_type": doc["file_type"],
                "file_size": len(doc["content"]),
                "file_path": f"seed/{doc_id}",
                "status": "ready",
                "chunk_count": 3,
            })

            paragraphs = [p.strip() for p in doc["content"].split("\n\n") if p.strip()]
            for i, para in enumerate(paragraphs):
                chunk_id = str(uuid.uuid4())
                await db.execute(text("""
                    INSERT INTO chunks (id, document_id, content, chunk_index, token_count)
                    VALUES (:id, :doc_id, :content, :idx, :tokens)
                """), {
                    "id": chunk_id,
                    "doc_id": doc_id,
                    "content": para,
                    "idx": i,
                    "tokens": len(para.split()),
                })

            print(f"Seeded: {doc['filename']} ({doc_id})")

        await db.commit()
        print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
