from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from back_app.database import get_session
from back_app import models
import csv
from io import StringIO
from datetime import datetime

router = APIRouter()

@router.post("/import/")
async def import_csv(
    file: UploadFile = File(...),
    user_id: int = 1,
    db: Session = Depends(get_session)
):
    contents = await file.read()
    decoded = contents.decode("utf-8")
    csv_reader = csv.DictReader(StringIO(decoded))

    importadas = 0
    puladas = 0

    for row in csv_reader:
        # Remove espaços extras nos nomes e valores das colunas
        row = {k.strip(): v.strip() for k, v in row.items()}

        try:
            data = datetime.strptime(row["Data"], "%d/%m/%Y").date()
            valor = float(row["Valor"].replace(",", "."))
            descricao = row["Descrição"]
            identificador = row.get("Identificador", None)

            if valor > 0:
                if identificador:
                    exists = db.query(models.Revenue).filter_by(identificador=identificador).first()
                    if exists:
                        puladas += 1
                        continue

                receita = models.Revenue(
                    name=descricao,
                    amount=valor,
                    user_id=user_id,
                    identificador=identificador
                )
                db.add(receita)

            elif valor < 0:
                if identificador:
                    exists = db.query(models.Expense).filter_by(identificador=identificador).first()
                    if exists:
                        puladas += 1
                        continue

                despesa = models.Expense(
                    name=descricao,
                    amount=abs(valor),
                    user_id=user_id,
                    identificador=identificador,
                    tag=None
                )
                db.add(despesa)

            importadas += 1

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao processar linha {row}: {e}")

    db.commit()
    return {"mensagem": "Importação finalizada", "importadas": importadas, "puladas": puladas}
