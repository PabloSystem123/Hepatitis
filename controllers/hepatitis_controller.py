from flask import Blueprint, jsonify, render_template, request

from Models.predictor import (
    ArtifactLoadError,
    BINARY_FEATURES,
    BINARY_NO_VALUE,
    BINARY_YES_VALUE,
    PredictorHepatico,
)

hepatic_bp = Blueprint("hepatitis", __name__)
predictor = PredictorHepatico()


@hepatic_bp.route("/", methods=["GET", "POST"])
def formulario_hepatic():
    error = None
    result = None
    values = predictor.example_payload()

    if request.method == "POST":
        values = {}
        for feature in predictor.feature_order:
            if feature in BINARY_FEATURES:
                values[feature] = (
                    BINARY_YES_VALUE if request.form.get(feature) else BINARY_NO_VALUE
                )
            else:
                values[feature] = request.form.get(feature, "")
        try:
            result = predictor.predict(values)
        except KeyError as missing:
            error = f"Campo obligatorio faltante: {missing.args[0]}"
        except ValueError:
            error = "Todos los valores deben ser números válidos."
        except ArtifactLoadError:
            error = "Error: Modelos no disponibles."
        except Exception as exc:  # pragma: no cover - UI guardrail
            error = f"Error procesando predicción: {exc}"

    return render_template(
        "hepatic_form.html",
        feature_order=predictor.feature_order,
        values=values,
        result=result,
        error=error,
        model_ready=predictor.ready,
        startup_error=predictor.startup_error,
        binary_fields=BINARY_FEATURES,
        binary_yes=BINARY_YES_VALUE,
        binary_no=BINARY_NO_VALUE,
    )


@hepatic_bp.route("/health", methods=["GET"])
def health_hepatic():
    status = "activo" if predictor.ready else "error"
    return (
        jsonify(
            {
                "status": status,
                "modelo_cargado": predictor.ready,
                "features_requeridas": predictor.feature_order,
                "detalle_error": str(predictor.startup_error) if predictor.startup_error else None,
            }
        ),
        200 if predictor.ready else 500,
    )


@hepatic_bp.route("/schema", methods=["GET"])
def schema_hepatic():
    if not predictor.ready:
        return (
            jsonify({"error": "Modelos no cargados", "detalles": str(predictor.startup_error)}),
            500,
        )

    return jsonify(predictor.schema()), 200


@hepatic_bp.route("/predict", methods=["POST"])
def predict_api_hepatic():
    if not predictor.ready:
        return jsonify({"error": "Modelos no disponibles"}), 500

    if not request.is_json:
        return jsonify({"error": "Requiere JSON en el cuerpo"}), 400

    payload = request.get_json()

    try:
        result = predictor.predict(payload)
    except KeyError as missing:
        return jsonify({"error": f"Campo faltante: {missing.args[0]}"}), 400
    except ValueError:
        return jsonify({"error": "Todos los valores deben ser numéricos"}), 400
    except Exception as exc:  # pragma: no cover - runtime guardrail
        return jsonify({"error": "Solicitud no procesable", "detalles": str(exc)}), 500

    return jsonify(result), 200
