from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from back_app.database import get_session
from back_app import models
from back_app.security import get_current_user
from back_app.models import User
import csv
from io import StringIO
from datetime import datetime

router = APIRouter()

@router.post("/import/")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    decoded = contents.decode("utf-8")
    csv_reader = csv.DictReader(StringIO(decoded))

    importadas = 0
    puladas = 0

    for row in csv_reader:
        row = {k.strip(): v.strip() for k, v in row.items()}

        try:
            # print(f"Processando linha: {row}")
            data = datetime.strptime(row["Data"], "%d/%m/%Y").date()
            valor = float(row["Valor"].replace(",", "."))
            descricao = row["Descrição"]
            identificador = row.get("Identificador", None)

            if valor > 0:
                if identificador:
                    exists = db.query(models.Revenue).filter_by(identificador=identificador).first()
                    if exists:
                        puladas += 1
                        # print(f"Receita com identificador {identificador} já existe. Pulando.")
                        continue

                receita = models.Revenue(
                    name=descricao,
                    amount=valor,
                    user_id=current_user.id,
                    identificador=identificador
                )
                db.add(receita)

            elif valor < 0:
                if identificador:
                    exists = db.query(models.Expense).filter_by(identificador=identificador).first()
                    if exists:
                        puladas += 1
                        # print(f"Despesa com identificador {identificador} já existe. Pulando.")
                        continue

                despesa = models.Expense(
                    name=descricao,
                    amount=abs(valor),
                    user_id=current_user.id,
                    identificador=identificador,
                    tag=None
                )
                db.add(despesa)

            importadas += 1

        except Exception as e:
            # print(f"Erro ao processar linha {row}: {e}")
            raise HTTPException(status_code=400, detail=f"Erro ao processar linha {row}: {e}")

    db.commit()
    # print(f"Importação finalizada. Importadas: {importadas}, Puladas: {puladas}")
    return {"mensagem": "Importação finalizada", "importadas": importadas, "puladas": puladas}
