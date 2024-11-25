import React, { useState } from "react";
import {
  Box,
  Button,
  Container,
  Typography,
  TextField,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from "@mui/material";

function App() {
  const [fileContent, setFileContent] = useState(""); // Contenido del archivo o texto escrito
  const [outputContent, setOutputContent] = useState(""); // Contenido del output
  const [fileName, setFileName] = useState(""); // Nombre del archivo seleccionado
  const [error, setError] = useState(null); // Manejo de errores
  const [showDialog, setShowDialog] = useState(false); // Muestra el cuadro de confirmación para reemplazo
  const [pendingFile, setPendingFile] = useState(null); // Archivo pendiente de cargar
  const [saveDialogOpen, setSaveDialogOpen] = useState(false); // Controla el diálogo para nombrar archivo
  const [customFileName, setCustomFileName] = useState(""); // Nombre personalizado para guardar el archivo

  const handleFileUpload = (event) => {
    const file = event.target.files[0];

    if (file) {
      if (!file.name.endsWith(".sps")) {
        setError("Por favor selecciona un archivo con extensión .sps");
        return;
      }

      if (fileContent.trim() !== "") {
        // Si hay contenido en el cuadro, pregunta antes de reemplazarlo
        setPendingFile(file);
        setShowDialog(true);
      } else {
        readFile(file);
      }
    }
  };

  const readFile = (file) => {
    setFileName(file.name); // Guarda el nombre del archivo
    setError(null); // Limpia errores anteriores
    const reader = new FileReader();
    reader.onload = (e) => {
      setFileContent(e.target.result); // Carga el contenido del archivo
    };
    reader.readAsText(file); // Lee el archivo como texto
  };

  const handleSave = () => {
    setCustomFileName(fileName || "nuevo-archivo.sps"); // Usa el nombre actual o un predeterminado
    setSaveDialogOpen(true); // Abre el cuadro de diálogo para nombrar el archivo
  };

  const saveFile = () => {
    const blob = new Blob([fileContent], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = customFileName.endsWith(".sps")
      ? customFileName
      : `${customFileName}.sps`; // Asegura la extensión
    link.click();
    setSaveDialogOpen(false); // Cierra el diálogo
  };

  const handleDialogClose = (saveBeforeReplace) => {
    setShowDialog(false);
    if (saveBeforeReplace) {
      handleSave(); // Guarda antes de reemplazar
    }
    if (pendingFile) {
      readFile(pendingFile); // Reemplaza el contenido con el nuevo archivo
      setPendingFile(null);
    }
  };

  return (
    <Container maxWidth={false} sx={{ bgcolor: "#00bce4", padding: 2 }}>
      <Typography variant="h1" gutterBottom sx={{ color: "white" }}>
        San Pedro Script Interpreter
      </Typography>

      <Box mb={5}>
        <Button
          variant="contained"
          component="label"
          sx={{ marginRight: 2, bgcolor: "white", color: "black" }}
        >
          Seleccionar archivo
          <input
            type="file"
            accept=".sps"
            hidden
            onChange={handleFileUpload}
          />
        </Button>

        <Button
          variant="contained"
          onClick={handleSave}
          sx={{ bgcolor: "white", color: "black" }}
        >
          Guardar archivo
        </Button>

        {fileName && (
          <Typography variant="body1" sx={{ color: "white", marginTop: 2 }}>
            <strong>Archivo seleccionado:</strong> {fileName}
          </Typography>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ marginBottom: 2 }}>
          {error}
        </Alert>
      )}

      {/* TextField para escribir el código */}
      <Typography variant="h6" sx={{ color: "white", marginBottom: 2 }}>
        Editor de código
      </Typography>
      <TextField
        multiline
        rows={15}
        fullWidth
        value={fileContent}
        onChange={(e) => setFileContent(e.target.value)} // Permite editar el contenido
        variant="outlined"
        placeholder="Aquí se escribe el código de SPScript"
        sx={{ bgcolor: "white", marginBottom: 3 }}
      />

      {/* TextField para el output */}
      <Typography variant="h6" sx={{ color: "white", marginBottom: 2 }}>
        Output
      </Typography>
      <TextField
        multiline
        rows={10}
        fullWidth
        value={outputContent}
        variant="outlined"
        placeholder="El output aparecerá aquí..."
        sx={{ bgcolor: "white" }}
        InputProps={{
          readOnly: true, // Campo de solo lectura
        }}
      />

      {/* Diálogo de confirmación para reemplazo */}
      <Dialog
        open={showDialog}
        onClose={() => handleDialogClose(false)}
      >
        <DialogTitle>Guardar cambios</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Tienes contenido escrito que será reemplazado si cargas un nuevo archivo.
            ¿Deseas guardarlo antes de continuar?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleDialogClose(false)} color="primary">
            No guardar
          </Button>
          <Button onClick={() => handleDialogClose(true)} color="primary" autoFocus>
            Guardar y reemplazar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Diálogo para nombrar el archivo */}
      <Dialog
        open={saveDialogOpen}
        onClose={() => setSaveDialogOpen(false)}
      >
        <DialogTitle>Guardar archivo</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Escribe el nombre que deseas para el archivo.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Nombre del archivo"
            fullWidth
            value={customFileName}
            onChange={(e) => setCustomFileName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)} color="primary">
            Cancelar
          </Button>
          <Button onClick={saveFile} color="primary">
            Guardar
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default App;
