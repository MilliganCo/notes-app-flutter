import 'package:geolocator/geolocator.dart';

Future<Position?> getCurrentLocation() async {
  try {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      print('Службы геолокации отключены.');
      return null;
    }

    LocationPermission permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      print('Нет разрешений на геолокацию.');
      return null;
    }

    return await Geolocator.getCurrentPosition();
  } catch (e) {
    print('Ошибка геолокации: $e');
    return null;
  }
}
