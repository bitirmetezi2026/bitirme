package com.example.caloriecalculator

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.common.FileUtil
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer
import java.nio.MappedByteBuffer

class FoodClassifier(context: Context) {
    private var interpreter: Interpreter
    private var labels: List<String>

    init {
        // 1. Modeli ve etiketleri "assets" klasöründen yükle
        // EĞER DOSYA İSİMLERİN FARKLIYSA BURAYI DÜZELT:
        val modelBuffer: MappedByteBuffer = FileUtil.loadMappedFile(context, "Food_Classification_EfficientNetB4.tflite")
        interpreter = Interpreter(modelBuffer)
        labels = FileUtil.loadLabels(context, "labels.txt")
    }

    fun classifyImage(bitmap: Bitmap): String {
        // 2. Resmi senin modelinin beklediği boyuta (380x380) getir
        val imageProcessor = ImageProcessor.Builder()
            .add(ResizeOp(380, 380, ResizeOp.ResizeMethod.BILINEAR))
            .build()

        // Resmi TensorImage formatına çevir (TFLite'ın anladığı dil)
        var tensorImage = TensorImage(org.tensorflow.lite.DataType.FLOAT32)
        tensorImage.load(bitmap)
        tensorImage = imageProcessor.process(tensorImage)

        // 3. Çıktı havuzunu hazırla (199 yemeğin olasılıkları buraya dolacak)
        val probabilityBuffer = TensorBuffer.createFixedSize(
            intArrayOf(1, 199),
            org.tensorflow.lite.DataType.FLOAT32
        )

        // 4. YAPAY ZEKAYI ÇALIŞTIR!
        interpreter.run(tensorImage.buffer, probabilityBuffer.buffer.rewind())

        // 5. En yüksek olasılıklı yemeği bul
        val probabilities = probabilityBuffer.floatArray
        var maxIndex = 0
        var maxProbability = probabilities[0]

        for (i in probabilities.indices) {
            if (probabilities[i] > maxProbability) {
                maxProbability = probabilities[i]
                maxIndex = i
            }
        }

        // Sonucu ve emin olma yüzdesini döndür (Örn: "iskender (%95)")
        val predictedFood = labels[maxIndex]
        val confidence = (maxProbability * 100).toInt()

        return "$predictedFood (%$confidence)"
    }

    // Uygulama kapanırken hafızayı temizlemek için
    fun close() {
        interpreter.close()
    }
}