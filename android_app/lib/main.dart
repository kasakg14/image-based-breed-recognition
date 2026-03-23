import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

void main() {
  runApp(const PashupahachanApp());
}

class PashupahachanApp extends StatefulWidget {
  const PashupahachanApp({super.key});

  @override
  State<PashupahachanApp> createState() => _PashupahachanAppState();
}

class _PashupahachanAppState extends State<PashupahachanApp> {
  String _languageCode = 'en';

  @override
  Widget build(BuildContext context) {
    final text = localizedText[_languageCode]!;
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: text.appName,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFEF6A3C),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFFFF7E8),
        fontFamily: 'sans-serif',
      ),
      home: HomeScreen(
        text: text,
        currentLanguage: _languageCode,
        onLanguageChanged: (value) {
          setState(() {
            _languageCode = value;
          });
        },
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    required this.text,
    required this.currentLanguage,
    required this.onLanguageChanged,
  });

  final AppText text;
  final String currentLanguage;
  final ValueChanged<String> onLanguageChanged;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ImagePicker _picker = ImagePicker();
  File? _selectedImage;
  PredictionResult? _prediction;
  bool _isLoading = false;

  Future<void> _pickImage(ImageSource source) async {
    final picked = await _picker.pickImage(source: source, imageQuality: 85);
    if (picked == null) return;

    setState(() {
      _selectedImage = File(picked.path);
      _prediction = null;
    });
  }

  Future<void> _runPrediction() async {
    if (_selectedImage == null) return;

    setState(() {
      _isLoading = true;
    });

    await Future<void>.delayed(const Duration(milliseconds: 900));

    setState(() {
      _prediction = mockPredictions[widget.currentLanguage] ?? mockPredictions['en'];
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final text = widget.text;
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _HeroCard(
                text: text,
                currentLanguage: widget.currentLanguage,
                onLanguageChanged: widget.onLanguageChanged,
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _InfoCard(
                      title: text.supportedBreeds,
                      value: '19',
                      subtitle: text.supportedBreedsSubtitle,
                      accent: const Color(0xFF2F7D4F),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _InfoCard(
                      title: text.modeLabel,
                      value: text.offlineMode,
                      subtitle: text.modeSubtitle,
                      accent: const Color(0xFF4BA3F2),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _UploadPanel(
                text: text,
                selectedImage: _selectedImage,
                isLoading: _isLoading,
                prediction: _prediction,
                onCameraTap: () => _pickImage(ImageSource.camera),
                onGalleryTap: () => _pickImage(ImageSource.gallery),
                onPredictTap: _runPrediction,
              ),
              const SizedBox(height: 16),
              _GuidanceCard(text: text),
            ],
          ),
        ),
      ),
    );
  }
}

class _HeroCard extends StatelessWidget {
  const _HeroCard({
    required this.text,
    required this.currentLanguage,
    required this.onLanguageChanged,
  });

  final AppText text;
  final String currentLanguage;
  final ValueChanged<String> onLanguageChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(28),
        gradient: const LinearGradient(
          colors: [Color(0xFFFFF5DC), Color(0xFFF8E8FF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: const [
          BoxShadow(
            color: Color(0x22000000),
            blurRadius: 24,
            offset: Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0x1F2F7D4F),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  text.kicker,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1,
                    color: Color(0xFF2F7D4F),
                  ),
                ),
              ),
              const Spacer(),
              DropdownButton<String>(
                value: currentLanguage,
                underline: const SizedBox.shrink(),
                items: const [
                  DropdownMenuItem(value: 'en', child: Text('English')),
                  DropdownMenuItem(value: 'hi', child: Text('हिंदी')),
                  DropdownMenuItem(value: 'mr', child: Text('मराठी')),
                ],
                onChanged: (value) {
                  if (value != null) onLanguageChanged(value);
                },
              ),
            ],
          ),
          const SizedBox(height: 18),
          Text(
            text.appName,
            style: const TextStyle(
              fontSize: 34,
              height: 1.0,
              fontWeight: FontWeight.w900,
              color: Color(0xFF182447),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            text.heroDescription,
            style: const TextStyle(
              fontSize: 16,
              height: 1.55,
              color: Color(0xFF5D6486),
            ),
          ),
          const SizedBox(height: 18),
          ClipRRect(
            borderRadius: BorderRadius.circular(22),
            child: AspectRatio(
              aspectRatio: 16 / 9,
              child: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Color(0xFF8FD2FF), Color(0xFFFFF2C5), Color(0xFF93C96E)],
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                  ),
                ),
                child: CustomPaint(
                  painter: FarmScenePainter(),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({
    required this.title,
    required this.value,
    required this.subtitle,
    required this.accent,
  });

  final String title;
  final String value;
  final String subtitle;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.82),
        borderRadius: BorderRadius.circular(22),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w800,
              letterSpacing: 1,
              color: Color(0xFF5D6486),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w900,
              color: accent,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            subtitle,
            style: const TextStyle(
              color: Color(0xFF5D6486),
              height: 1.45,
            ),
          ),
        ],
      ),
    );
  }
}

class _UploadPanel extends StatelessWidget {
  const _UploadPanel({
    required this.text,
    required this.selectedImage,
    required this.isLoading,
    required this.prediction,
    required this.onCameraTap,
    required this.onGalleryTap,
    required this.onPredictTap,
  });

  final AppText text;
  final File? selectedImage;
  final bool isLoading;
  final PredictionResult? prediction;
  final VoidCallback onCameraTap;
  final VoidCallback onGalleryTap;
  final VoidCallback onPredictTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.86),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            text.uploadTitle,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w800,
              color: Color(0xFF1B2440),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            text.uploadSubtitle,
            style: const TextStyle(
              color: Color(0xFF5D6486),
              height: 1.5,
            ),
          ),
          const SizedBox(height: 16),
          if (selectedImage != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(18),
              child: Image.file(
                selectedImage!,
                height: 220,
                width: double.infinity,
                fit: BoxFit.cover,
              ),
            )
          else
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 26),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0x554BA3F2)),
                gradient: const LinearGradient(
                  colors: [Color(0xFFFDFEFF), Color(0xFFF0F7FF)],
                ),
              ),
              child: Column(
                children: [
                  const Icon(Icons.photo_camera_back_rounded, size: 42, color: Color(0xFFEF6A3C)),
                  const SizedBox(height: 10),
                  Text(
                    text.noImageSelected,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF1B2440),
                    ),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  onPressed: onCameraTap,
                  icon: const Icon(Icons.camera_alt_outlined),
                  label: Text(text.camera),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onGalleryTap,
                  icon: const Icon(Icons.photo_library_outlined),
                  label: Text(text.gallery),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: selectedImage == null || isLoading ? null : onPredictTap,
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Text(isLoading ? text.analyzing : text.predict),
              ),
            ),
          ),
          if (prediction != null) ...[
            const SizedBox(height: 18),
            _PredictionCard(text: text, result: prediction!),
          ],
        ],
      ),
    );
  }
}

class _PredictionCard extends StatelessWidget {
  const _PredictionCard({
    required this.text,
    required this.result,
  });

  final AppText text;
  final PredictionResult result;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0x2637A95A), Color(0x30F4B942), Color(0x224BA3F2)],
            ),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                text.mostLikely,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1,
                  color: Color(0xFF5D6486),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                result.primaryBreed,
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF182447),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${text.confidence}: ${result.confidence}',
                style: const TextStyle(
                  color: Color(0xFF5D6486),
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                result.summary,
                style: const TextStyle(
                  color: Color(0xFF5D6486),
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                text.uniqueFeature,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1,
                  color: Color(0xFF5D6486),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                result.uniqueTrait,
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF1B2440),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                result.valueNote,
                style: const TextStyle(
                  color: Color(0xFF5D6486),
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        Text(
          text.otherMatches,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w800,
            color: Color(0xFF1B2440),
          ),
        ),
        const SizedBox(height: 8),
        ...result.otherMatches.map(
          (match) => Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FBFF),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    match.label,
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF1B2440),
                    ),
                  ),
                ),
                Text(
                  match.score,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF2F7D4F),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _GuidanceCard extends StatelessWidget {
  const _GuidanceCard({required this.text});

  final AppText text;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.86),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            text.guidanceTitle,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w800,
              color: Color(0xFF1B2440),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            text.guidanceBody,
            style: const TextStyle(
              color: Color(0xFF5D6486),
              height: 1.55,
            ),
          ),
        ],
      ),
    );
  }
}

class FarmScenePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final hillPaint = Paint()
      ..shader = const LinearGradient(
        colors: [Color(0xFF89C66C), Color(0xFF4D9650)],
      ).createShader(Rect.fromLTWH(0, size.height * 0.35, size.width, size.height * 0.65));
    final fieldPaint = Paint()
      ..shader = const LinearGradient(
        colors: [Color(0xFFD2B25F), Color(0xFF7CA348)],
      ).createShader(Rect.fromLTWH(0, size.height * 0.58, size.width, size.height * 0.42));

    canvas.drawPath(
      Path()
        ..moveTo(0, size.height * 0.56)
        ..quadraticBezierTo(size.width * 0.22, size.height * 0.40, size.width * 0.45, size.height * 0.48)
        ..quadraticBezierTo(size.width * 0.72, size.height * 0.26, size.width, size.height * 0.44)
        ..lineTo(size.width, size.height)
        ..lineTo(0, size.height)
        ..close(),
      hillPaint,
    );

    canvas.drawPath(
      Path()
        ..moveTo(0, size.height * 0.72)
        ..quadraticBezierTo(size.width * 0.30, size.height * 0.62, size.width * 0.58, size.height * 0.70)
        ..quadraticBezierTo(size.width * 0.83, size.height * 0.60, size.width, size.height * 0.74)
        ..lineTo(size.width, size.height)
        ..lineTo(0, size.height)
        ..close(),
      fieldPaint,
    );

    final sunPaint = Paint()..color = const Color(0xFFFFD35E);
    canvas.drawCircle(Offset(size.width * 0.82, size.height * 0.20), size.width * 0.06, sunPaint);

    final cowBody = Paint()..color = const Color(0xFFF3E4D2);
    final patchPaint = Paint()..color = const Color(0xFFC98546);
    final legPaint = Paint()..color = const Color(0xFF7B5B44);

    final bodyRect = Rect.fromCenter(
      center: Offset(size.width * 0.48, size.height * 0.62),
      width: size.width * 0.34,
      height: size.height * 0.24,
    );
    canvas.drawOval(bodyRect, cowBody);
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(size.width * 0.67, size.height * 0.52),
        width: size.width * 0.14,
        height: size.height * 0.14,
      ),
      cowBody,
    );
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(size.width * 0.42, size.height * 0.55),
        width: size.width * 0.09,
        height: size.height * 0.06,
      ),
      patchPaint,
    );
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(size.width * 0.55, size.height * 0.66),
        width: size.width * 0.10,
        height: size.height * 0.07,
      ),
      patchPaint,
    );

    for (final x in [0.40, 0.49, 0.61, 0.69]) {
      canvas.drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTWH(size.width * x, size.height * 0.69, size.width * 0.015, size.height * 0.18),
          const Radius.circular(12),
        ),
        legPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class AppText {
  const AppText({
    required this.appName,
    required this.kicker,
    required this.heroDescription,
    required this.supportedBreeds,
    required this.supportedBreedsSubtitle,
    required this.modeLabel,
    required this.modeSubtitle,
    required this.offlineMode,
    required this.uploadTitle,
    required this.uploadSubtitle,
    required this.noImageSelected,
    required this.camera,
    required this.gallery,
    required this.predict,
    required this.analyzing,
    required this.mostLikely,
    required this.confidence,
    required this.uniqueFeature,
    required this.otherMatches,
    required this.guidanceTitle,
    required this.guidanceBody,
  });

  final String appName;
  final String kicker;
  final String heroDescription;
  final String supportedBreeds;
  final String supportedBreedsSubtitle;
  final String modeLabel;
  final String modeSubtitle;
  final String offlineMode;
  final String uploadTitle;
  final String uploadSubtitle;
  final String noImageSelected;
  final String camera;
  final String gallery;
  final String predict;
  final String analyzing;
  final String mostLikely;
  final String confidence;
  final String uniqueFeature;
  final String otherMatches;
  final String guidanceTitle;
  final String guidanceBody;
}

class PredictionResult {
  const PredictionResult({
    required this.primaryBreed,
    required this.confidence,
    required this.summary,
    required this.uniqueTrait,
    required this.valueNote,
    required this.otherMatches,
  });

  final String primaryBreed;
  final String confidence;
  final String summary;
  final String uniqueTrait;
  final String valueNote;
  final List<PredictionMatch> otherMatches;
}

class PredictionMatch {
  const PredictionMatch({
    required this.label,
    required this.score,
  });

  final String label;
  final String score;
}

const localizedText = {
  'en': AppText(
    appName: 'पशुपहचान',
    kicker: 'Indian Livestock Vision',
    heroDescription: 'Breed recognition for Indian cattle and buffaloes with an Android-friendly workflow for field use.',
    supportedBreeds: 'Supported breeds',
    supportedBreedsSubtitle: 'Indian cattle and buffalo breed library starter.',
    modeLabel: 'Recognition Mode',
    modeSubtitle: 'Prepared for offline-first field usage.',
    offlineMode: 'Offline Ready',
    uploadTitle: 'Upload and analyze',
    uploadSubtitle: 'Capture a farm image from camera or choose one from gallery.',
    noImageSelected: 'No image selected yet',
    camera: 'Use Camera',
    gallery: 'Choose Gallery',
    predict: 'Predict Breed',
    analyzing: 'Analyzing...',
    mostLikely: 'Most likely match',
    confidence: 'Confidence',
    uniqueFeature: 'Unique breed feature',
    otherMatches: 'Other matches',
    guidanceTitle: 'Field guidance',
    guidanceBody: 'Next step: connect this UI to an API or an on-device TensorFlow Lite model for real Android prediction.',
  ),
  'hi': AppText(
    appName: 'पशुपहचान',
    kicker: 'भारतीय पशुधन दृष्टि',
    heroDescription: 'भारतीय गाय और भैंस नस्ल पहचान के लिए एंड्रॉइड आधारित फील्ड उपयोग ऐप।',
    supportedBreeds: 'समर्थित नस्लें',
    supportedBreedsSubtitle: 'भारतीय गाय और भैंस नस्लों के लिए प्रारंभिक लाइब्रेरी।',
    modeLabel: 'पहचान मोड',
    modeSubtitle: 'ऑफलाइन उपयोग के लिए तैयार संरचना।',
    offlineMode: 'ऑफलाइन तैयार',
    uploadTitle: 'तस्वीर अपलोड करें और जांचें',
    uploadSubtitle: 'कैमरा से फोटो लें या गैलरी से चुनें।',
    noImageSelected: 'अभी तक कोई तस्वीर चुनी नहीं गई',
    camera: 'कैमरा',
    gallery: 'गैलरी',
    predict: 'नस्ल पहचानें',
    analyzing: 'विश्लेषण हो रहा है...',
    mostLikely: 'सबसे संभावित मिलान',
    confidence: 'विश्वास स्तर',
    uniqueFeature: 'विशेष नस्ल पहचान',
    otherMatches: 'अन्य मिलान',
    guidanceTitle: 'मैदानी सुझाव',
    guidanceBody: 'अगला कदम: इस UI को API या TensorFlow Lite मॉडल से जोड़कर वास्तविक एंड्रॉइड भविष्यवाणी देना।',
  ),
  'mr': AppText(
    appName: 'पशुपहचान',
    kicker: 'भारतीय पशुधन दृष्टी',
    heroDescription: 'भारतीय गायी आणि म्हशींच्या जाती ओळखण्यासाठी अँड्रॉइड आधारित फील्ड अॅप.',
    supportedBreeds: 'समर्थित जाती',
    supportedBreedsSubtitle: 'भारतीय गाय आणि म्हैस जातींसाठी सुरुवातीची लायब्ररी.',
    modeLabel: 'ओळख मोड',
    modeSubtitle: 'ऑफलाइन वापरासाठी तयार रचना.',
    offlineMode: 'ऑफलाइन तयार',
    uploadTitle: 'फोटो अपलोड करा आणि तपासा',
    uploadSubtitle: 'कॅमेऱ्यातून फोटो घ्या किंवा गॅलरीतून निवडा.',
    noImageSelected: 'अजून कोणताही फोटो निवडलेला नाही',
    camera: 'कॅमेरा',
    gallery: 'गॅलरी',
    predict: 'जात ओळखा',
    analyzing: 'विश्लेषण सुरू आहे...',
    mostLikely: 'सर्वात संभाव्य जुळणी',
    confidence: 'विश्वास पातळी',
    uniqueFeature: 'विशेष जातीची खूण',
    otherMatches: 'इतर जुळणी',
    guidanceTitle: 'मैदानी मार्गदर्शन',
    guidanceBody: 'पुढचा टप्पा: या UI ला API किंवा TensorFlow Lite मॉडेलशी जोडून खरे अँड्रॉइड prediction देणे.',
  ),
};

const mockPredictions = {
  'en': PredictionResult(
    primaryBreed: 'Gir',
    confidence: '92%',
    summary: 'Likely Gir based on ear shape, forehead profile, and coat pattern similarity.',
    uniqueTrait: 'Long pendulous ears with a prominent domed forehead.',
    valueNote: 'Gir cattle are strongly associated with heat tolerance and dairy value.',
    otherMatches: [
      PredictionMatch(label: 'Sahiwal', score: '83%'),
      PredictionMatch(label: 'Kankrej', score: '77%'),
      PredictionMatch(label: 'Red Sindhi', score: '69%'),
    ],
  ),
  'hi': PredictionResult(
    primaryBreed: 'Gir',
    confidence: '92%',
    summary: 'कान की बनावट, माथे की प्रोफाइल और रंग पैटर्न के आधार पर यह गिर नस्ल जैसी लगती है।',
    uniqueTrait: 'लंबे लटकते कान और उभरा हुआ गोल माथा इसकी खास पहचान हैं।',
    valueNote: 'गिर नस्ल गर्मी सहनशीलता और डेयरी उपयोगिता के लिए जानी जाती है।',
    otherMatches: [
      PredictionMatch(label: 'Sahiwal', score: '83%'),
      PredictionMatch(label: 'Kankrej', score: '77%'),
      PredictionMatch(label: 'Red Sindhi', score: '69%'),
    ],
  ),
  'mr': PredictionResult(
    primaryBreed: 'Gir',
    confidence: '92%',
    summary: 'कानांची रचना, कपाळाचा आकार आणि रंगसाम्य पाहता ही गिर जात असण्याची शक्यता जास्त आहे.',
    uniqueTrait: 'लांब झुकणारे कान आणि उठावदार गोल कपाळ ही याची प्रमुख खूण आहे.',
    valueNote: 'गिर जात उष्णता सहनशक्ती आणि दुधाळ उपयोगासाठी ओळखली जाते.',
    otherMatches: [
      PredictionMatch(label: 'Sahiwal', score: '83%'),
      PredictionMatch(label: 'Kankrej', score: '77%'),
      PredictionMatch(label: 'Red Sindhi', score: '69%'),
    ],
  ),
};
