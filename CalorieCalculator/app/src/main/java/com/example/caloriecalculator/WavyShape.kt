package com.example.caloriecalculator

import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Outline
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.LayoutDirection

// Referans tasarımdaki alttan gelen dalga için güncellendi
class WavyShape : Shape {
    override fun createOutline(
        size: Size,
        layoutDirection: LayoutDirection,
        density: Density
    ): Outline {
        val path = Path().apply {
            // Çizime sol alttan başla
            moveTo(0f, size.height)
            // Sol üst köşeye git, ama biraz aşağıdan başla ki kavis oradan başlasın
            lineTo(0f, size.height * 0.2f)
            // Yumuşak kavisi çiz
            quadraticBezierTo(
                x1 = size.width / 2, y1 = 0f, // Kontrol noktası: Ekranın ortası, en üst
                x2 = size.width, y2 = size.height * 0.2f // Bitiş noktası: Sağ üst, biraz aşağıda
            )
            // Sağ alt köşeye in
            lineTo(size.width, size.height)
            // Şekli kapat
            close()
        }
        return Outline.Generic(path)
    }
}